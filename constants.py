# API Configuration
BASE_URL = "https://ipinfo.io/{ip}?token={token}"
MAX_CONCURRENT_REQUESTS = 5
REQUEST_TIMEOUT = 10  # seconds


# Error Messages
MISSING_TOKEN_MSG = "Missing API_TOKEN in environment"
INVALID_IP_MSG = "Invalid IP: {error}"
API_LIMIT_MSG = "API limit exceeded"
API_ERROR_MSG = "API Error: {error}"
NETWORK_ERROR_MSG = "Network error: {error}"
UNEXPECTED_ERROR_MSG = "Unexpected error: {error}"
INVALID_RESPONSE_MSG = "Invalid API response format"


# UI Messages
WELCOME_MSG = "IP Info Fetcher (Ctrl+C to quit)"
GOODBYE_MSG = "\nGoodbye!"
PROMPT_MSG = "Enter IPs: "
ERROR_MSG = "Error: {error}"
FATAL_ERROR_MSG = "Fatal error occurred: {error}"


# EXITING COMMANDS
EXITING_COMMANDS = ("exit", "quit", "q")
