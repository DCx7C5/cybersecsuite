"""Scans module enums."""

from enum import Enum


class ScanType(str, Enum):
    """Types of security scans."""

    VULNERABILITY = "vulnerability"
    COMPLIANCE = "compliance"
    CONFIGURATION = "configuration"
    MALWARE = "malware"
    WEB_APPLICATION = "web_application"
    NETWORK = "network"
    CODE = "code"
    CONTAINER = "container"


class ScanStatus(str, Enum):
    """Scan lifecycle status."""

    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityRating(str, Enum):
    """Finding severity."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

