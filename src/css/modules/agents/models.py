"""Agent data models — configuration and result structures using msgspec."""

from __future__ import annotations

import msgspec
from datetime import datetime
from typing import Any


class TokenUsage(msgspec.Struct):
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


class AgentConfig(msgspec.Struct):
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


class AgentResult(msgspec.Struct):
    """Result from agent execution.
    
    Attributes:
        agent_id: ID of the executing agent
        session_id: Conversation session ID
        response: Final text response from agent
        tool_calls: Any tools the agent attempted to use
        usage: Token usage statistics
        duration_ms: Time taken for execution
        provider_used: Which provider was actually used
        stop_reason: Why execution stopped (end_turn, tool_use, max_tokens, etc.)
        executed_at: Timestamp of execution
    """
    agent_id: str
    session_id: str
    response: str
    tool_calls: list[dict[str, Any]] = msgspec.field(default_factory=list)
    usage: TokenUsage | None = None
    duration_ms: float = 0.0
    provider_used: str = "unknown"
    stop_reason: str = "end_turn"
    executed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.executed_at is None:
            object.__setattr__(self, 'executed_at', datetime.now())


class AgentTurn(msgspec.Struct):
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
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)


class ConversationContext(msgspec.Struct):
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
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)

    def __post_init__(self) -> None:
        now = datetime.now()
        if self.created_at is None:
            object.__setattr__(self, 'created_at', now)
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', now)
