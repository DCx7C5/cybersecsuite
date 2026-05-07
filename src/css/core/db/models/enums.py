"""All enums for cybersecsuite database models."""

from enum import Enum


class RedBlueMode(str, Enum):
    """Blue team vs red team mode."""
    BLUE = "blue"
    RED = "red"
    PURPLE = "purple"


class SessionMode(str, Enum):
    """Session operation mode."""
    DEVELOPMENT = "development"
    BLUE = "blue"
    RED = "red"
    PURPLE = "purple"


class AuditAction(str, Enum):
    """Audit log action types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    START = "start"
    STOP = "stop"
    MODE_SWITCH = "mode_switch"
    READ = "read"
    SCHEMA_CREATE = "schema_create"
    SCHEMA_DROP = "schema_drop"
    SEED = "seed"
    HEALTH_CHECK = "health_check"


class Severity(str, Enum):
    """Finding severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Confidence(str, Enum):
    """Investigation confidence levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CONFIRMED = "confirmed"


class FindingStatus(str, Enum):
    """Security finding status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    INVESTIGATING = "investigating"


class IOCStatus(str, Enum):
    """Indicator of Compromise status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLEARED = "cleared"
