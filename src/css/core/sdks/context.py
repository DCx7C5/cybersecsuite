"""Context types for conversation and model execution.

Separates user/conversation context (what we're talking about)
from model context (what the model can do).

Uses msgspec.Struct for efficient serialization/deserialization.
"""

import msgspec
from datetime import datetime, timezone
from typing import Any

from css.core.base.messages import BaseMessage


class ConversationContext(msgspec.Struct, frozen=True, kw_only=True):
    """What we're talking about with the user.

    Persists across turns, tracks conversation state.
    """

    session_id: str
    user_id: str
    messages: list[BaseMessage] = msgspec.field(default_factory=list)
    turn_number: int = 0
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            object.__setattr__(self, 'created_at', now)
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', now)

    def add_message(self, message: BaseMessage) -> None:
        new_messages = [*self.messages, message]
        object.__setattr__(self, 'messages', new_messages)
        object.__setattr__(self, 'turn_number', self.turn_number + 1)
        object.__setattr__(self, 'updated_at', datetime.now(timezone.utc))

    def get_last_user_message(self) -> BaseMessage | None:
        for msg in reversed(self.messages):
            if msg.role.value == "user":
                return msg
        return None

    def get_last_assistant_message(self) -> BaseMessage | None:
        for msg in reversed(self.messages):
            if msg.role.value == "assistant":
                return msg
        return None


class ModelContext(msgspec.Struct, frozen=True, kw_only=True):
    """What a model can do and how much it costs."""

    provider: str
    model_name: str
    max_tokens: int = 4000
    context_window: int = 4000
    capabilities: list[str] = msgspec.field(default_factory=list)
    cost_per_1k_tokens: float = 0.0
    estimated_latency_ms: float = 0.0
    rate_limit_rpm: int | None = None
    rate_limit_tpm: int | None = None
    batch_support: bool = False
    vision_capable: bool = False
    tool_use_capable: bool = False
    discovered_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.discovered_at is None:
            object.__setattr__(self, 'discovered_at', datetime.now(timezone.utc))

    def effective_cost(self, tokens: int) -> float:
        return (tokens / 1000.0) * self.cost_per_1k_tokens


class ExecutionContext(msgspec.Struct, frozen=True, kw_only=True):
    """Combined context for a single LLM execution.

    Merges conversation and model context for complete picture.
    """

    conversation: ConversationContext
    model: ModelContext
    execution_id: str = msgspec.field(default_factory=lambda: str(__import__("uuid").uuid4()))
    started_at: datetime | None = None
    ended_at: datetime | None = None
    tokens_used: int = 0
    cost: float = 0.0
    error: str | None = None

    def __post_init__(self) -> None:
        if self.started_at is None:
            object.__setattr__(self, 'started_at', datetime.now(timezone.utc))

    def set_completed(self, tokens_used: int = 0) -> None:
        object.__setattr__(self, 'ended_at', datetime.now(timezone.utc))
        object.__setattr__(self, 'tokens_used', tokens_used)
        object.__setattr__(self, 'cost', self.model.effective_cost(tokens_used))

    def set_failed(self, error: str) -> None:
        object.__setattr__(self, 'ended_at', datetime.now(timezone.utc))
        object.__setattr__(self, 'error', error)

    def get_duration_seconds(self) -> float | None:
        if self.ended_at is None or self.started_at is None:
            return None
        return (self.ended_at - self.started_at).total_seconds()


class ContextConfig(msgspec.Struct, frozen=True, kw_only=True):
    """Configuration for context handling."""

    max_conversation_turns: int = 100
    max_conversation_age_hours: int = 24
    capability_cache_ttl_hours: int = 24
    cost_estimate_variance_pct: float = 0.1
    log_all_executions: bool = True
    trace_expensive_calls: bool = True
