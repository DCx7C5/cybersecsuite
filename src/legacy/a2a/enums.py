"""
A2A Protocol enums and constants.
Based on the Google Agent-to-Agent (A2A) protocol specification.
"""
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


class AuthScheme(str, Enum):
    """Supported authentication schemes."""
    NONE = "none"
    ED25519 = "ed25519"
    BEARER = "bearer"
    API_KEY = "api_key"

