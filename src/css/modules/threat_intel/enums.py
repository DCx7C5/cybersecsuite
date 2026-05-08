"""Threat intelligence enums."""

from enum import Enum


class IOCType(str, Enum):
    """Indicator of Compromise types."""

    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    REGISTRY_KEY = "registry_key"
    USER_AGENT = "user_agent"


class ThreatLevel(str, Enum):
    """IOC threat level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


__all__ = ["IOCType", "ThreatLevel"]
