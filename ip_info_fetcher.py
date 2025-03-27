import asyncio
import aiohttp
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import quote
from http import HTTPStatus
from log_config import setup_logger
from validation import IPValidator
from constants import *

logger = setup_logger()


@dataclass
class IPInfoResult:
    """A dataclass to store the result of an IP information lookup.

    Attributes:
        ip (str): The IP address that was queried
        data (Dict): The returned data from the API
        error (Optional[str]): Error message if the lookup failed
        status_code (Optional[int]): HTTP status code of the response
    """

    ip: str
    data: Dict
    error: Optional[str] = None
    status_code: Optional[int] = None


class IPInfoAPI:
    """Handles communication with the IP information API."""

    def __init__(self):
        """Initialize the API client and get the authentication token."""
        self.token = self._get_token()
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

    @staticmethod
    def _get_token() -> str:
        """Retrieve the API token from environment variables.

        Returns:
            str: The API token

        Raises:
            ValueError: If the API token is not found in environment variables
        """
        token = os.getenv("API_TOKEN")
        if not token:
            logger.error(MISSING_TOKEN_MSG)
            raise ValueError(MISSING_TOKEN_MSG)
        return token

    async def __aenter__(self):
        """Asynchronous context manager entry point.

        Returns:
            IPInfoAPI: The initialized API client
        """
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, *exc):
        """Asynchronous context manager exit point.

        Ensures proper cleanup of the aiohttp session.
        """
        if self.session:
            await self.session.close()

    def _build_url(self, ip: str) -> str:
        """Construct the API URL for a given IP address.

        Args:
            ip (str): The IP address to query

        Returns:
            str: The complete API URL
        """
        return BASE_URL.format(ip=quote(ip), token=self.token)

    async def fetch_info(self, ip: str) -> IPInfoResult:
        """Fetch information about a single IP address from the API.

        Args:
            ip (str): The IP address to lookup

        Returns:
            IPInfoResult: The result of the lookup operation
        """
        logger.debug(f"Starting IP lookup for {ip}")
        valid, validation_error = IPValidator.validate(ip)

        if not valid:
            logger.warning(f"Invalid IP detected: {ip} - {validation_error}")
            return IPInfoResult(
                ip,
                {},
                INVALID_IP_MSG.format(error=validation_error),
                HTTPStatus.BAD_REQUEST.value,
            )

        logger.debug(f"Building URL for {ip}")
        url = self._build_url(ip)

        try:
            logger.info(f"Making API request for {ip}")
            async with self.session.get(url) as response:
                logger.debug(f"Received response status {response.status} for {ip}")

                # Handle HTML responses (usually errors)
                if "text/html" in response.headers.get("Content-Type", ""):
                    text = await response.text()
                    logger.warning(
                        f"Unexpected HTML response for {ip}: {text[:200]}..."
                    )

                    if "limit exceeded" in text.lower():
                        logger.error("API rate limit exceeded")
                        return IPInfoResult(
                            ip, {}, API_LIMIT_MSG, HTTPStatus.TOO_MANY_REQUESTS.value
                        )
                    return IPInfoResult(
                        ip, {}, API_ERROR_MSG.format(error=text[:100]), response.status
                    )

                # Process JSON response
                try:
                    logger.debug(f"Attempting to parse JSON for {ip}")
                    data = await response.json()

                    if response.status == HTTPStatus.OK.value:
                        logger.info(f"Successfully retrieved data for {ip}")
                        return IPInfoResult(ip, data, None, response.status)

                    logger.warning(
                        f"API error for {ip}: {data.get('error', 'Unknown error')}"
                    )
                    return IPInfoResult(
                        ip,
                        {},
                        data.get("error", API_ERROR_MSG.format(error="Unknown error")),
                        response.status,
                    )

                except aiohttp.ContentTypeError as content_error:
                    logger.error(f"ContentTypeError for {ip}: {str(content_error)}")
                    return IPInfoResult(
                        ip,
                        {},
                        INVALID_RESPONSE_MSG,
                        HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    )

        except aiohttp.ClientError as client_err:
            logger.error(f"Network error for {ip}: {str(client_err)}")
            return IPInfoResult(
                ip,
                {},
                NETWORK_ERROR_MSG.format(error=str(client_err)),
                HTTPStatus.INTERNAL_SERVER_ERROR.value,
            )
        except Exception as unexpected_err:
            logger.critical(f"Unexpected error for {ip}: {str(unexpected_err)}")
            return IPInfoResult(
                ip,
                {},
                UNEXPECTED_ERROR_MSG.format(error=str(unexpected_err)),
                HTTPStatus.INTERNAL_SERVER_ERROR.value,
            )


class IPProcessor:
    """Processes multiple IP addresses concurrently."""

    @staticmethod
    async def process(ips: List[str]) -> List[IPInfoResult]:
        """Process a list of IP addresses concurrently.

        Args:
            ips (List[str]): List of IP addresses to process

        Returns:
            List[IPInfoResult]: Results for all IP addresses
        """
        logger.info(f"Starting batch processing of {len(ips)} IPs")
        async with IPInfoAPI() as api:
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
            logger.debug(
                f"Configured semaphore with {MAX_CONCURRENT_REQUESTS} max concurrent requests"
            )

            async def fetch(ip: str) -> IPInfoResult:
                """Fetch information for a single IP address.

                Args:
                    ip (str): The IP address to lookup

                Returns:
                    IPInfoResult: The lookup result
                """
                async with semaphore:
                    logger.debug(f"Acquired semaphore for {ip}")
                    result = await api.fetch_info(ip)
                    logger.debug(f"Completed processing for {ip}")
                    return result

            logger.info("Launching all IP lookups")
            results = await asyncio.gather(*[fetch(ip) for ip in ips])

            success_count = sum(1 for r in results if not r.error)
            logger.info(f"Batch complete. Success: {success_count}/{len(ips)}")
            return results


class CLI:
    """Handles command line interface operations."""

    @staticmethod
    def parse_input(input_str: str) -> List[str]:
        """Parse user input into a list of IP addresses.

        Args:
            input_str (str): Raw user input containing IP addresses

        Returns:
            List[str]: Cleaned list of IP addresses
        """
        return [ip.strip() for ip in input_str.replace(",", " ").split() if ip.strip()]

    @staticmethod
    def display(results: List[IPInfoResult]):
        """Display the results to the user.

        Args:
            results (List[IPInfoResult]): List of results to display
        """
        for result in results:
            print(f"\nIP: {result.ip}")
            if result.error:
                print(f"  Error ({result.status_code}): {result.error}")
            else:
                for k, v in result.data.items():
                    print(f"  {k}: {v}")


async def main():
    """Main entry point for the IP information fetcher application."""
    print(WELCOME_MSG)
    while True:
        try:
            user_input = input(f"{PROMPT_MSG} or q, exit, quit to finish").strip()

            # Check for exit commands
            if user_input.lower() in EXITING_COMMANDS:
                print("\n" + GOODBYE_MSG)
                break

            if not user_input:
                continue

            ips = CLI.parse_input(user_input)
            results = await IPProcessor.process(ips)
            CLI.display(results)

        except KeyboardInterrupt:
            print("\n" + GOODBYE_MSG)
            break
        except Exception as error:
            print(ERROR_MSG.format(error=str(error)))
            logger.error(f"Error in main loop: {str(error)}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(FATAL_ERROR_MSG.format(error=str(e)))
        print(FATAL_ERROR_MSG.format(error=str(e)))
