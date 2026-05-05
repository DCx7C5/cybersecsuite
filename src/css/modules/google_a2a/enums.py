from enum import Enum


class TaskState(str, Enum):
    """Lifecycle states of an A2A task."""

    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class MessageRole(str, Enum):
    """Role of a message sender."""

    USER = "user"
    AGENT = "agent"


class PartType(str, Enum):
    """Type of a message part."""

    TEXT = "text"
    FILE = "file"
    DATA = "data"


class StreamState(str, Enum):
    """Streaming lifecycle states."""

    CLEAR = "clear"  # No external request pending
    PAUSED = "paused"  # Waiting for external context
    RUNNING = "running"  # Actively streaming


class ResponseInjectionStrategy(str, Enum):
    """Strategy for injecting external response into streaming context."""

    PREPEND = "prepend"  # Inject at beginning of system context (highest priority)
    INJECT = "inject"  # Append to last assistant message (lower priority)
    CHAIN = "chain"  # Ask model to incorporate in next turn (slowest)
