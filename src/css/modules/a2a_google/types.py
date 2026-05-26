"""a2a_google typed value objects and protocols."""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any, Protocol, TypeAlias, runtime_checkable

import msgspec

from .enums import MessageRole, PartType, StreamState, TaskState

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
A2AToolFunction: TypeAlias = Callable[[JsonObject], Awaitable[JsonObject] | JsonObject]


class TextPart(msgspec.Struct, frozen=True, kw_only=True):
    """Plain text content part."""

    type: PartType = PartType.TEXT
    text: str = ""
    metadata: dict[str, Any] | None = None


class FileContent(msgspec.Struct, frozen=True, kw_only=True):
    """File content (inline or by URI)."""

    name: str | None = None
    mime_type: str | None = None
    bytes: str | None = None
    uri: str | None = None


class FilePart(msgspec.Struct, frozen=True, kw_only=True):
    """File attachment part."""

    file: FileContent
    type: PartType = PartType.FILE
    metadata: dict[str, Any] | None = None


class DataPart(msgspec.Struct, frozen=True, kw_only=True):
    """Structured JSON data part."""

    data: dict[str, Any]
    type: PartType = PartType.DATA
    metadata: dict[str, Any] | None = None


Part: TypeAlias = TextPart | FilePart | DataPart


class Message(msgspec.Struct, frozen=True, kw_only=True):
    """A single message in a task conversation."""

    role: MessageRole
    parts: list[Part] = msgspec.field(default_factory=list)
    metadata: dict[str, Any] | None = None


class TaskArtifact(msgspec.Struct, frozen=True, kw_only=True):
    """Output artifact produced by an A2A task."""

    parts: list[Part] = msgspec.field(default_factory=list)
    name: str | None = None
    description: str | None = None
    index: int = 0
    append: bool | None = None
    last_chunk: bool | None = None
    metadata: dict[str, Any] | None = None


class TaskStatus(msgspec.Struct, frozen=True, kw_only=True):
    """Current status of a task."""

    state: TaskState
    message: Message | None = None
    timestamp: datetime = msgspec.field(default_factory=lambda: datetime.now(UTC))


class Task(msgspec.Struct, frozen=True, kw_only=True):
    """An A2A task unit."""

    id: str
    status: TaskStatus
    session_id: str | None = None
    history: list[Message] = msgspec.field(default_factory=list)
    artifacts: list[TaskArtifact] = msgspec.field(default_factory=list)
    metadata: dict[str, Any] | None = None


class JSONRPCError(msgspec.Struct, frozen=True, kw_only=True):
    """JSON-RPC 2.0 error object."""

    code: int
    message: str
    data: JsonObject | str | None = None


class JSONRPCRequest(msgspec.Struct, frozen=True, kw_only=True):
    """JSON-RPC 2.0 request object."""

    method: str
    jsonrpc: str = "2.0"
    params: dict[str, object] | None = None
    id: str | int | None = None


class JSONRPCResponse(msgspec.Struct, frozen=True, kw_only=True):
    """JSON-RPC 2.0 response object."""

    jsonrpc: str = "2.0"
    result: dict[str, object] | None = None
    error: JSONRPCError | None = None
    id: str | int | None = None


class TaskSendParams(msgspec.Struct, frozen=True, kw_only=True):
    """Parameters for tasks/create method."""

    id: str
    message: dict[str, object]
    session_id: str | None = None


class TaskQueryParams(msgspec.Struct, frozen=True, kw_only=True):
    """Parameters for tasks/get method."""

    id: str


class A2AConfig(msgspec.Struct, frozen=True, kw_only=True):
    """Runtime configuration for a2a_google routing behavior."""

    allow_cancel_completed: bool = False


class PauseRequest(msgspec.Struct, frozen=True, kw_only=True):
    """Pause request payload for stream control."""

    request_id: str
    reason: str | None = None


class ResponseInjection(msgspec.Struct, frozen=True, kw_only=True):
    """External response payload to inject into stream output."""

    content: str
    source: str


class StreamingState(msgspec.Struct, frozen=True, kw_only=True):
    """Mutable stream state snapshot."""

    state: StreamState = StreamState.RUNNING
    reason: str | None = None


@runtime_checkable
class AgentCardProtocol(Protocol):
    """Structural type for card payload objects."""

    agent_id: str


@runtime_checkable
class A2ACommunicatorProtocol(Protocol):
    """Structural type for A2A communicators used by endpoints."""

    agent_id: str

    async def create_task(
        self,
        task_id: str,
        message: dict[str, object],
        session_id: str | None = None,
    ) -> object:
        """Create a task."""

    async def get_task(self, task_id: str) -> object:
        """Get a task by id."""


@runtime_checkable
class StreamingController(Protocol):
    """Protocol for stream state control implementations."""

    async def pause(self, request: PauseRequest) -> StreamingState:
        """Pause a stream."""

    async def resume(self, request_id: str) -> StreamingState:
        """Resume a stream."""


class ToolMetadata(msgspec.Struct, frozen=True, kw_only=True):
    """Registered A2A tool metadata."""

    name: str
    description: str
    input_schema: JsonObject
    fn: A2AToolFunction
