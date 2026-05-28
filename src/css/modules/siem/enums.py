"""SIEM module enums."""

from enum import Enum


class SiemSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SiemSource(str, Enum):
    SPLUNK = "splunk"
    CROWDSTRIKE = "crowdstrike"
    SENTINELONE = "sentinelone"
    GENERIC = "generic"

