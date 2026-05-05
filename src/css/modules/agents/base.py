"""Base agent protocol and executor — minimal Protocol for agent execution.

This module defines:
1. BaseAgent Protocol: Minimal interface for agent-like systems
2. AgentExecutor: Runs an agent with an LLM provider

The design avoids dataclass+ABC mixing by using Protocol (PEP 544).
Each agent (even external/remote) just needs to implement execute().
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable
import asyncio
import logging
from datetime import datetime

log = logging.getLogger(__name__)


@runtime_checkable
class BaseAgent(Protocol):
    """Minimal Protocol for agent-like systems.
    
    An agent is anything that can:
    - Accept a prompt/context
    - Return a structured result
    
    No inheritance needed; duck typing allows external agents to be treated as BaseAgent.
    """

    async def execute(
        self,
        prompt: str,
        context: dict | None = None,
        **kwargs,
    ) -> AgentResult:
        """Execute the agent with a prompt.
        
        Args:
            prompt: User prompt or instruction
            context: Optional conversation context
            **kwargs: Provider-specific options (temperature, max_tokens, etc.)
            
        Returns:
            AgentResult with response, reasoning trace, and metadata
            
        Raises:
            AgentExecutionError: If execution fails
        """
        ...


class AgentResult:
    """Structured result from agent execution.
    
    Attributes:
        response: Final agent response (text)
        thinking: Internal reasoning chain (if available)
        tool_calls: Any tools the agent tried to use
        stop_reason: Why execution stopped (end_turn, tool_use, max_tokens, etc.)
        input_tokens: Token count for prompt
        output_tokens: Token count for response
        duration_ms: Execution time in milliseconds
        executed_at: Timestamp of execution
        provider: Which LLM provider was used
        model: Which model variant
    """

    def __init__(
        self,
        response: str,
        thinking: str | None = None,
        tool_calls: list[dict] | None = None,
        stop_reason: str = "end_turn",
        input_tokens: int = 0,
        output_tokens: int = 0,
        duration_ms: float = 0,
        provider: str = "unknown",
        model: str = "unknown",
    ):
        self.response = response
        self.thinking = thinking
        self.tool_calls = tool_calls or []
        self.stop_reason = stop_reason
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.duration_ms = duration_ms
        self.executed_at = datetime.now()
        self.provider = provider
        self.model = model

    def to_dict(self) -> dict:
        """Convert to serializable dict."""
        return {
            "response": self.response,
            "thinking": self.thinking,
            "tool_calls": self.tool_calls,
            "stop_reason": self.stop_reason,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "duration_ms": self.duration_ms,
            "executed_at": self.executed_at.isoformat(),
            "provider": self.provider,
            "model": self.model,
        }

    def __repr__(self) -> str:
        return (
            f"AgentResult(provider={self.provider}, model={self.model}, "
            f"response={self.response[:50]}..., "
            f"tokens={self.input_tokens}→{self.output_tokens}, "
            f"duration_ms={self.duration_ms:.1f})"
        )


class AgentExecutor:
    """Executes a BaseAgent with an LLM provider.
    
    Wires together:
    - Agent: What to execute
    - Provider client: How to execute (OpenAI, Anthropic, etc.)
    - Context: Conversation history
    - Instrumentation: Events, logging, tracing
    """

    def __init__(self, provider_client, provider: str, model: str):
        """Initialize executor.
        
        Args:
            provider_client: Async client for the LLM provider (e.g., AsyncOpenAI)
            provider: Provider name (openai, anthropic, etc.)
            model: Model identifier (gpt-4, claude-opus, etc.)
        """
        self.client = provider_client
        self.provider = provider
        self.model = model

    async def execute(
        self,
        prompt: str,
        context: dict | None = None,
        **kwargs,
    ) -> AgentResult:
        """Execute agent prompt against LLM.
        
        Args:
            prompt: User prompt
            context: Optional conversation context
            **kwargs: Provider-specific options
            
        Returns:
            AgentResult with response and metadata
        """
        raise NotImplementedError(
            "AgentExecutor.execute() must be implemented by provider-specific subclass"
        )
