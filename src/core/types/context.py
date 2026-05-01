"""Context types for conversation and model execution.

Separates user/conversation context (what we're talking about)
from model context (what the model can do).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .api_services import Message


@dataclass
class ConversationContext(BaseModel):
    """What we're talking about with the user.

    Persists across turns, tracks conversation state.
    """

    session_id: str = Field(..., description="Unique conversation session")
    user_id: str = Field(..., description="User making the request")
    messages: list[Message] = Field(default_factory=list, description="Conversation history")
    turn_number: int = Field(default=0, description="Current turn (0-indexed)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata (tags, etc.)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        use_enum_values = False

    def add_message(self, message: Message) -> None:
        """Add message to conversation history."""
        self.messages.append(message)
        self.turn_number += 1
        self.updated_at = datetime.utcnow()

    def get_last_user_message(self) -> Optional[Message]:
        """Get most recent user message."""
        for msg in reversed(self.messages):
            if msg.role.value == "user":
                return msg
        return None

    def get_last_assistant_message(self) -> Optional[Message]:
        """Get most recent assistant message."""
        for msg in reversed(self.messages):
            if msg.role.value == "assistant":
                return msg
        return None


@dataclass
class ModelContext(BaseModel):
    """What a model can do and how much it costs.

    Model-specific capabilities, limits, and pricing.
    """

    provider: str = Field(..., description="Provider name (e.g., 'openai', 'anthropic')")
    model_name: str = Field(..., description="Model identifier (e.g., 'gpt-4', 'claude-3-sonnet')")
    max_tokens: int = Field(default=4000, description="Max tokens per request")
    context_window: int = Field(default=4000, description="Total context window size")
    capabilities: list[str] = Field(default_factory=list, description="Supported capabilities")
    cost_per_1k_tokens: float = Field(default=0.0, description="Cost per 1k tokens")
    estimated_latency_ms: float = Field(default=0.0, description="Expected response latency")
    rate_limit_rpm: Optional[int] = Field(default=None, description="Requests per minute limit")
    rate_limit_tpm: Optional[int] = Field(default=None, description="Tokens per minute limit")
    batch_support: bool = Field(default=False, description="Supports batch API?")
    vision_capable: bool = Field(default=False, description="Supports vision input?")
    tool_use_capable: bool = Field(default=False, description="Supports tool calling?")
    discovered_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        use_enum_values = False

    def effective_cost(self, tokens: int) -> float:
        """Calculate cost for token count."""
        return (tokens / 1000.0) * self.cost_per_1k_tokens


@dataclass
class ExecutionContext(BaseModel):
    """Combined context for a single LLM execution.

    Merges conversation and model context for complete picture.
    """

    conversation: ConversationContext = Field(..., description="What we're talking about")
    model: ModelContext = Field(..., description="What the model can do")
    execution_id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(default=None)
    tokens_used: int = Field(default=0, description="Tokens consumed in execution")
    cost: float = Field(default=0.0, description="Actual cost incurred")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        """Pydantic config."""

        use_enum_values = False

    def set_completed(self, tokens_used: int = 0) -> None:
        """Mark execution as completed."""
        self.ended_at = datetime.utcnow()
        self.tokens_used = tokens_used
        self.cost = self.model.effective_cost(tokens_used)

    def set_failed(self, error: str) -> None:
        """Mark execution as failed."""
        self.ended_at = datetime.utcnow()
        self.error = error

    def get_duration_seconds(self) -> Optional[float]:
        """Get execution duration in seconds."""
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at).total_seconds()


@dataclass
class ContextConfig(BaseModel):
    """Configuration for context handling."""

    # Conversation context
    max_conversation_turns: int = Field(default=100, description="Max turns per conversation")
    max_conversation_age_hours: int = Field(default=24, description="Max age before archiving")

    # Model context
    capability_cache_ttl_hours: int = Field(default=24, description="Cache model capabilities for this long")
    cost_estimate_variance_pct: float = Field(default=0.1, description="10% variance on cost estimates")

    # Execution tracking
    log_all_executions: bool = Field(default=True, description="Log all LLM calls?")
    trace_expensive_calls: bool = Field(default=True, description="Trace calls costing >$0.10?")

    class Config:
        """Pydantic config."""

        extra = "allow"  # Allow forward-compatible fields
