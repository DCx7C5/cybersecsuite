"""Core A2A streaming state machine and config types."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import ResponseInjectionStrategy, StreamState


@dataclass
class PauseRequest:
    """Request to pause ModelA stream and query ModelB."""

    request_id: str = field(default_factory=lambda: str(uuid4()))
    question: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    source_model: str = ""
    target_model: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    timeout_seconds: int = 30


class ResponseInjection(BaseModel):
    """External response to inject into ModelA's stream."""

    response_text: str = Field(..., description="ModelB's response to inject")
    source_model: str = Field(..., description="Which model answered")
    priority: int = Field(default=100)
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    strategy: ResponseInjectionStrategy = Field(default=ResponseInjectionStrategy.PREPEND)

    model_config = {"use_enum_values": True}


@dataclass
class StreamingState:
    """Complete state of a streaming session with A2A coordination."""

    session_id: str = field(default_factory=lambda: str(uuid4()))
    state: StreamState = StreamState.CLEAR
    current_pause_request: PauseRequest | None = None
    pending_injections: list[ResponseInjection] = field(default_factory=list)
    buffer: list[str] = field(default_factory=list)
    timestamp_paused: datetime | None = None
    timestamp_resumed: datetime | None = None


class StreamingController:
    """Protocol for controlling A2A streaming lifecycle."""

    async def pause_and_request(
        self,
        question: str,
        context: dict[str, Any] | None = None,
        target_model: str | None = None,
        timeout_seconds: int = 30,
    ) -> str: ...

    async def inject_response(self, injection: ResponseInjection) -> None: ...

    async def resume_stream(self) -> None: ...

    def get_state(self) -> StreamingState: ...


@dataclass
class A2AConfig:
    """Configuration for A2A streaming behaviour."""

    injection_strategy: ResponseInjectionStrategy = ResponseInjectionStrategy.PREPEND
    max_buffer_size: int = 10_000
    pause_timeout_seconds: int = 30
    request_timeout_seconds: int = 60
    max_retries: int = 2
    retry_backoff_seconds: float = 1.0
    injected_response_prefix: str = "[External Context] "
    system_context_position: str = "prepend"


@dataclass
class ToolMetadata:
    """Metadata for a registered A2A tool."""

    name: str
    description: str
    schema: dict[str, Any]
    fn: object


class AgentCard(BaseModel):
    """A2A Agent identity card."""

    name: str
    description: str
    version: str = "1.0.0"
    url: str | None = None


__all__ = [
    "PauseRequest",
    "ResponseInjection",
    "StreamingState",
    "StreamingController",
    "A2AConfig",
    "ToolMetadata",
    "AgentCard",
]
