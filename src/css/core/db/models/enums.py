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


class ScopeLevel(str, Enum):
    """Scope hierarchy level."""
    GLOBAL = "global"
    PROJECT = "project"
    SESSION = "session"
    TEAM = "team"


class OrchestratorStatus(str, Enum):
    """Orchestrator instance status."""
    STARTING = "starting"
    IDLE = "idle"
    BUSY = "busy"
    PAUSED = "paused"
    STOPPED = "stopped"
    CRASHED = "crashed"


class UserRoles(str, Enum):
    """User roles."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"





class TaskAssignmentStatus(str, Enum):
    """Task assignment status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# ProviderTypes: not a static Enum — loaded dynamically from api_services.yml at startup (see tracker 'provider-types-dynamic')