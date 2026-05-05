"""A2A Protocol Pydantic models for google_a2a module."""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from .enums import TaskState, MessageRole, PartType


# ─── Parts ────────────────────────────────────────────────────────────────────


class TextPart(BaseModel):
    """Plain text content part."""

    type: PartType = PartType.TEXT
    text: str
    metadata: Optional[Dict[str, Any]] = None


class FileContent(BaseModel):
    """File content (inline or by URI)."""

    name: Optional[str] = None
    mime_type: Optional[str] = None
    bytes: Optional[str] = None  # base64-encoded
    uri: Optional[str] = None


class FilePart(BaseModel):
    """File attachment part."""

    type: PartType = PartType.FILE
    file: FileContent
    metadata: Optional[Dict[str, Any]] = None


class DataPart(BaseModel):
    """Structured JSON data part."""

    type: PartType = PartType.DATA
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


Part = Union[TextPart, FilePart, DataPart]


# ─── Message ──────────────────────────────────────────────────────────────────


class Message(BaseModel):
    """A single message in a task conversation."""

    role: MessageRole
    parts: List[Part]
    metadata: Optional[Dict[str, Any]] = None


# ─── Artifact ─────────────────────────────────────────────────────────────────


class TaskArtifact(BaseModel):
    """Output artifact produced by an agent task."""

    name: Optional[str] = None
    description: Optional[str] = None
    parts: List[Part]
    index: int = 0
    append: Optional[bool] = None
    last_chunk: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


# ─── Task Status ──────────────────────────────────────────────────────────────


class TaskStatus(BaseModel):
    """Current status of a task."""

    state: TaskState
    message: Optional[Message] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ─── Task ──────────────────────────────────────────────────────────────────────


class Task(BaseModel):
    """An A2A task unit."""

    id: str
    session_id: Optional[str] = None
    status: TaskStatus
    history: Optional[List[Message]] = None
    artifacts: Optional[List[TaskArtifact]] = None
    metadata: Optional[Dict[str, Any]] = None
