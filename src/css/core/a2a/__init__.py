"""Core A2A protocol — shared enums, models, and streaming types."""

from .enums import MessageRole, PartType, ResponseInjectionStrategy, StreamState, TaskState
from .models import DataPart, FilePart, FileContent, Message, Part, Task, TaskArtifact, TaskStatus, TextPart
from .types import A2AConfig, AgentCard, PauseRequest, ResponseInjection, StreamingController, StreamingState, ToolMetadata

__all__ = [
    # enums
    "TaskState",
    "MessageRole",
    "PartType",
    "StreamState",
    "ResponseInjectionStrategy",
    # models
    "TextPart",
    "FileContent",
    "FilePart",
    "DataPart",
    "Part",
    "Message",
    "TaskArtifact",
    "TaskStatus",
    "Task",
    # types
    "PauseRequest",
    "ResponseInjection",
    "StreamingState",
    "StreamingController",
    "A2AConfig",
    "ToolMetadata",
    "AgentCard",
]
