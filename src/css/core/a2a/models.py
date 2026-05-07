"""Core A2A protocol models — Google A2A wire format types."""

from datetime import datetime, timezone
from typing import Any, Union

from pydantic import BaseModel, Field

from .enums import MessageRole, PartType, TaskState


class TextPart(BaseModel):
    """Plain text content part."""

    type: PartType = PartType.TEXT
    text: str
    metadata: dict[str, Any] | None = None


class FileContent(BaseModel):
    """File content (inline or by URI)."""

    name: str | None = None
    mime_type: str | None = None
    bytes: str | None = None  # base64-encoded
    uri: str | None = None


class FilePart(BaseModel):
    """File attachment part."""

    type: PartType = PartType.FILE
    file: FileContent
    metadata: dict[str, Any] | None = None


class DataPart(BaseModel):
    """Structured JSON data part."""

    type: PartType = PartType.DATA
    data: dict[str, Any]
    metadata: dict[str, Any] | None = None


Part = Union[TextPart, FilePart, DataPart]


class Message(BaseModel):
    """A single message in a task conversation."""

    role: MessageRole
    parts: list[Part]
    metadata: dict[str, Any] | None = None


class TaskArtifact(BaseModel):
    """Output artifact produced by an agent task."""

    name: str | None = None
    description: str | None = None
    parts: list[Part]
    index: int = 0
    append: bool | None = None
    last_chunk: bool | None = None
    metadata: dict[str, Any] | None = None


class TaskStatus(BaseModel):
    """Current status of a task."""

    state: TaskState
    message: Message | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Task(BaseModel):
    """An A2A task unit."""

    id: str
    session_id: str | None = None
    status: TaskStatus
    history: list[Message] | None = None
    artifacts: list[TaskArtifact] | None = None
    metadata: dict[str, Any] | None = None


__all__ = [
    "TextPart",
    "FileContent",
    "FilePart",
    "DataPart",
    "Part",
    "Message",
    "TaskArtifact",
    "TaskStatus",
    "Task",
]
