"""a2a_google typed value objects and protocols."""

from collections.abc import Awaitable, Callable
from typing import Protocol, runtime_checkable

import msgspec
from pydantic import BaseModel

from .enums import StreamState

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
type JsonObject = dict[str, JsonValue]
type A2AToolFunction = Callable[[JsonObject], Awaitable[JsonObject] | JsonObject]


class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 error object."""

    code: int
    message: str
    data: JsonObject | str | None = None


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request object."""

    jsonrpc: str = "2.0"
    method: str
    params: dict[str, object] | None = None
    id: str | int | None = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response object."""

    jsonrpc: str = "2.0"
    result: dict[str, object] | None = None
    error: JSONRPCError | None = None
    id: str | int | None = None


class TaskSendParams(BaseModel):
    """Parameters for tasks/create method."""

    id: str
    message: dict[str, object]
    session_id: str | None = None


class TaskQueryParams(BaseModel):
    """Parameters for tasks/get method."""

    id: str


class A2AConfig(BaseModel):
    """Runtime configuration for a2a_google routing behavior."""

    allow_cancel_completed: bool = False


class PauseRequest(BaseModel):
    """Pause request payload for stream control."""

    request_id: str
    reason: str | None = None


class ResponseInjection(BaseModel):
    """External response payload to inject into stream output."""

    content: str
    source: str


class StreamingState(BaseModel):
    """Mutable stream state snapshot."""

    state: StreamState = StreamState.RUNNING
    reason: str | None = None


@runtime_checkable
class AgentCardProtocol(Protocol):
    """Structural type for card payload objects."""

    def model_dump(self, mode: str = "python") -> dict[str, object]:
        """Serialize card to dict."""


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


class ToolMetadata(msgspec.Struct):
    """Registered A2A tool metadata."""

    name: str
    description: str
    input_schema: JsonObject
    fn: A2AToolFunction
