"""Core A2A protocol enums — shared by css_a2a and google_a2a."""

from enum import Enum


class TaskState(str, Enum):
    """Lifecycle states of an A2A task."""

    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    PAUSED = "paused"


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

    CLEAR = "clear"
    PAUSED = "paused"
    RUNNING = "running"


class ResponseInjectionStrategy(str, Enum):
    """Strategy for injecting external response into streaming context."""

    PREPEND = "prepend"
    INJECT = "inject"
    CHAIN = "chain"


__all__ = [
    "TaskState",
    "MessageRole",
    "PartType",
    "StreamState",
    "ResponseInjectionStrategy",
]
