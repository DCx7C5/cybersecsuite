"""Chat enumerations."""

from enum import Enum


class ChatRole(str, Enum):
    """Role of a chat participant."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessageType(str, Enum):
    """Type of chat message."""
    TEXT = "text"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    SYSTEM = "system"


class ChatStatus(str, Enum):
    """Status of a chat session."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
