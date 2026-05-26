"""Agent data models — configuration and result structures using msgspec."""


import msgspec
from datetime import datetime


class TokenUsage(msgspec.Struct, frozen=True, kw_only=True):
    """Token usage statistics.
    
    Attributes:
        input_tokens: Tokens consumed by prompt
        output_tokens: Tokens generated in response
        total_tokens: Sum of input + output
    """
    input_tokens: int
    output_tokens: int
    total_tokens: int = 0

    def __post_init__(self) -> None:
        # Recalculate total
        if self.total_tokens == 0:
            object.__setattr__(self, 'total_tokens', self.input_tokens + self.output_tokens)


class AgentConfig(msgspec.Struct, frozen=True, kw_only=True):
    """Agent configuration and initialization parameters.
    
    Attributes:
        agent_id: Unique agent identifier
        name: Human-readable agent name
        provider: LLM provider (openai, anthropic, etc.)
        model: Model identifier (gpt-4, claude-opus, etc.)
        system_prompt: System prompt/instructions for the agent
        tools: List of tool IDs available to this agent
        skills: List of skill tags/categories
        max_tokens: Maximum output tokens per response
        temperature: Sampling temperature (0-1, None for default)
    """
    agent_id: str
    name: str
    provider: str
    model: str
    system_prompt: str
    tools: list[str] = msgspec.field(default_factory=list)
    skills: list[str] = msgspec.field(default_factory=list)
    max_tokens: int = 2048
    temperature: float | None = None


class AgentResult(msgspec.Struct, frozen=True, kw_only=True):
    """Result from agent execution.
    
    Canonical result type shared by AgentExecutor and conversation turns.
    """
    agent_id: str = ""
    session_id: str = ""
    response: str = ""
    thinking: str | None = None
    tool_calls: list[dict[str, object]] = msgspec.field(default_factory=list)
    usage: TokenUsage | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: float = 0.0
    provider: str = "unknown"
    model: str = "unknown"
    stop_reason: str = "end_turn"
    executed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.executed_at is None:
            object.__setattr__(self, 'executed_at', datetime.now())
        if self.usage is None and (self.input_tokens or self.output_tokens):
            object.__setattr__(
                self,
                'usage',
                TokenUsage(
                    input_tokens=self.input_tokens,
                    output_tokens=self.output_tokens,
                ),
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "response": self.response,
            "thinking": self.thinking,
            "tool_calls": self.tool_calls,
            "usage": {
                "input_tokens": self.usage.input_tokens,
                "output_tokens": self.usage.output_tokens,
                "total_tokens": self.usage.total_tokens,
            } if self.usage else None,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "duration_ms": self.duration_ms,
            "provider": self.provider,
            "model": self.model,
            "stop_reason": self.stop_reason,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"AgentResult(provider={self.provider}, model={self.model}, "
            f"response={self.response[:50]}..., "
            f"tokens={self.input_tokens}→{self.output_tokens}, "
            f"duration_ms={self.duration_ms:.1f})"
        )


class AgentTurn(msgspec.Struct, frozen=True, kw_only=True):
    """Single turn in agent conversation.
    
    Represents one request-response cycle in a multi-turn conversation.
    
    Attributes:
        turn_index: 0-based turn number
        request: User request/prompt
        result: Agent's response (AgentResult)
        metadata: Optional additional turn metadata
    """
    turn_index: int
    request: str
    result: AgentResult
    metadata: dict[str, object] = msgspec.field(default_factory=dict)


class ConversationContext(msgspec.Struct, frozen=True, kw_only=True):
    """Conversation context and history.
    
    Attributes:
        session_id: Unique conversation session ID
        agent_id: Agent participating in this conversation
        turns: List of conversation turns
        created_at: Conversation creation time
        updated_at: Last update time
        metadata: Optional context metadata (user_id, scope, etc.)
    """
    session_id: str
    agent_id: str
    turns: list[AgentTurn] = msgspec.field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict[str, object] = msgspec.field(default_factory=dict)

    def __post_init__(self) -> None:
        now = datetime.now()
        if self.created_at is None:
            object.__setattr__(self, 'created_at', now)
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', now)
