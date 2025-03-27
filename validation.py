import ipaddress
from typing import Tuple


class IPValidator:
    @staticmethod
    def validate(ip: str) -> Tuple[bool, str]:
        try:
            ipaddress.ip_address(ip)
            return True, ""
        except ValueError as e:
            return False, str(e)
