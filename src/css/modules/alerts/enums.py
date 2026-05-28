"""Alerts module enums."""

from enum import Enum


class DeliveryStatus(str, Enum):
    """Alert delivery status."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """Alert delivery channels."""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"

