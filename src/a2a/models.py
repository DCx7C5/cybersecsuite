"""
A2A Protocol Pydantic models.
Implements the Google Agent-to-Agent (A2A) protocol data structures.
"""


from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from a2a.enums import TaskState, MessageRole, PartType, AuthScheme


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
    bytes: Optional[str] = None   # base64-encoded
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


# ─── Task ─────────────────────────────────────────────────────────────────────

class Task(BaseModel):
    """An A2A task unit."""
    id: str
    session_id: Optional[str] = None
    status: TaskStatus
    history: Optional[List[Message]] = None
    artifacts: Optional[List[TaskArtifact]] = None
    metadata: Optional[Dict[str, Any]] = None


# ─── Task Request / Response ──────────────────────────────────────────────────

class TaskSendParams(BaseModel):
    """Parameters for sending a task."""
    id: str
    session_id: Optional[str] = None
    message: Message
    history_length: Optional[int] = None
    push_notification: Optional[PushNotificationConfig] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskQueryParams(BaseModel):
    """Parameters for querying task status."""
    id: str
    history_length: Optional[int] = None


class TaskIdParams(BaseModel):
    """Minimal task ID params."""
    id: str


# ─── Push Notifications ───────────────────────────────────────────────────────

class PushNotificationConfig(BaseModel):
    """Configuration for push notifications on task updates."""
    url: str
    token: Optional[str] = None
    authentication: Optional[Dict[str, Any]] = None


class TaskPushNotificationConfig(BaseModel):
    """Push notification config linked to a task."""
    id: str
    push_notification_config: PushNotificationConfig


# ─── Agent Card ───────────────────────────────────────────────────────────────

class AgentCapabilities(BaseModel):
    """What an agent supports."""
    streaming: bool = False
    push_notifications: bool = False
    state_transition_history: bool = False


class AgentAuthentication(BaseModel):
    """Authentication configuration for an agent."""
    schemes: List[AuthScheme] = [AuthScheme.NONE]
    credentials: Optional[str] = None


class AgentSkill(BaseModel):
    """A capability or skill the agent provides."""
    id: str
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    input_modes: Optional[List[str]] = None
    output_modes: Optional[List[str]] = None


class AgentCard(BaseModel):
    """Agent identity and capability descriptor (served at /.well-known/agent.json)."""
    name: str
    description: Optional[str] = None
    url: str
    version: str = "0.1.0"
    documentation_url: Optional[str] = None
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    authentication: AgentAuthentication = Field(default_factory=AgentAuthentication)
    default_input_modes: List[str] = ["text/plain"]
    default_output_modes: List[str] = ["text/plain"]
    skills: List[AgentSkill] = Field(default_factory=list)
    provider: Optional[Dict[str, str]] = None
    icon_url: Optional[str] = None


# ─── JSON-RPC ─────────────────────────────────────────────────────────────────

class JSONRPCRequest(BaseModel):
    """A2A JSON-RPC 2.0 request."""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class JSONRPCError(BaseModel):
    """JSON-RPC error object."""
    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(BaseModel):
    """A2A JSON-RPC 2.0 response."""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None


# ─── A2A Error Codes ──────────────────────────────────────────────────────────

class A2AErrorCodes:
    """Standard A2A JSON-RPC error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    TASK_NOT_FOUND = -32001
    TASK_NOT_CANCELABLE = -32002
    PUSH_NOTIFICATION_NOT_SUPPORTED = -32003
    UNSUPPORTED_OPERATION = -32004
    CONTENT_TYPE_NOT_SUPPORTED = -32005
    AUTH_REQUIRED = -32006


# Forward reference resolution
TaskSendParams.model_rebuild()

