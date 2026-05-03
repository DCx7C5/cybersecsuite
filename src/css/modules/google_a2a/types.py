"""A2A streaming state machine for model-to-model collaboration.

Handles pausing ModelA, requesting context from ModelB, and resuming with injected response.
Supports bidirectional streaming with external context injection via PREPEND strategy.

This module is part of the A2A module package and should be imported from:
  from modules.google_a2a import A2AConfig, StreamState, ResponseInjection, etc.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import StreamState, ResponseInjectionStrategy


@dataclass
class PauseRequest:
    """Request to pause ModelA stream and query ModelB."""

    request_id: str = field(default_factory=lambda: str(uuid4()))
    question: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    source_model: str = ""  # Which model is requesting
    target_model: Optional[str] = None  # Which model to ask (None = auto-select)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    timeout_seconds: int = 30


class ResponseInjection(BaseModel):
    """External response to inject into ModelA's stream.

    Uses PREPEND strategy: response is added to beginning of system context
    to ensure highest AI priority and natural incorporation.
    """

    response_text: str = Field(..., description="ModelB's response to inject")
    source_model: str = Field(..., description="Which model answered")
    priority: int = Field(default=100, description="Context priority (higher = more attention)")
    request_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Links to PauseRequest"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    strategy: ResponseInjectionStrategy = Field(
        default=ResponseInjectionStrategy.PREPEND,
        description="How to inject into context",
    )

    class Config:
        """Pydantic config for serialization."""

        use_enum_values = True


@dataclass
class StreamingState:
    """Complete state of a streaming session with A2A coordination."""

    session_id: str = field(default_factory=lambda: str(uuid4()))
    state: StreamState = StreamState.CLEAR
    current_pause_request: Optional[PauseRequest] = None
    pending_injections: list[ResponseInjection] = field(default_factory=list)
    buffer: list[str] = field(default_factory=list)  # Paused stream buffer
    timestamp_paused: Optional[datetime] = None
    timestamp_resumed: Optional[datetime] = None


class StreamingController:
    """Protocol for controlling A2A streaming lifecycle.

    Manages pause/resume operations and response injection into active streams.
    """

    async def pause_and_request(
        self,
        question: str,
        context: Optional[dict[str, Any]] = None,
        target_model: Optional[str] = None,
        timeout_seconds: int = 30,
    ) -> str:
        """Pause ModelA, request context from ModelB, resume with response.

        Args:
            question: Question to ask external model
            context: Additional context for the request
            target_model: Which model to query (None = auto-select)
            timeout_seconds: Max time to wait for response

        Returns:
            ModelB's response text (will be injected via PREPEND)

        Raises:
            TimeoutError: If ModelB doesn't respond in time
            RuntimeError: If not currently streaming
        """
        pass

    async def inject_response(self, injection: ResponseInjection) -> None:
        """Inject external response into paused stream.

        Called after pause_and_request() gets response from ModelB.

        Args:
            injection: ResponseInjection with text, source, priority

        Strategy: Response is prepended to system context before resuming.
        This ensures it gets highest priority from the AI and is naturally
        incorporated into the ongoing response.
        """
        pass

    async def resume_stream(self) -> None:
        """Resume ModelA streaming after response injection.

        Called after inject_response() to continue the stream.
        ModelA will naturally incorporate injected context via PREPEND strategy.
        """
        pass

    def get_state(self) -> StreamingState:
        """Get current streaming state for monitoring/debugging."""
        pass


@dataclass
class A2AConfig:
    """Configuration for A2A streaming behavior."""

    # Response injection strategy (locked: PREPEND for Phase 0.0+)
    injection_strategy: ResponseInjectionStrategy = ResponseInjectionStrategy.PREPEND

    # Pause/resume tuning
    max_buffer_size: int = 10_000  # Max tokens to buffer while paused
    pause_timeout_seconds: int = 30  # How long to wait for ModelB
    request_timeout_seconds: int = 60  # How long pause_and_request can take

    # Retry policy
    max_retries: int = 2
    retry_backoff_seconds: float = 1.0

    # Context preparation
    injected_response_prefix: str = "[External Context] "
    system_context_position: str = "prepend"  # Where to insert in system context

    class Config:
        """Allow extra fields for forward compatibility."""

        extra = "allow"


__all__ = [
    "StreamState",
    "ResponseInjectionStrategy",
    "PauseRequest",
    "ResponseInjection",
    "StreamingState",
    "StreamingController",
    "A2AConfig",
]
