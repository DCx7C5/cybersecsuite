"""google_a2a enums."""

from enum import Enum, IntEnum


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
    """Streaming lifecycle for response injection."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ResponseInjectionStrategy(str, Enum):
    """How external content is merged into the model response stream."""

    PREPEND = "prepend"
    APPEND = "append"
    REPLACE = "replace"


class A2AErrorCode(IntEnum):
    """A2A JSON-RPC error codes."""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
