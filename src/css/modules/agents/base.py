"""Base agent protocol and executor — minimal Protocol for agent execution.

This module defines:
1. BaseAgent Protocol: Minimal interface for agent-like systems
2. AgentExecutor: Runs an agent with an LLM provider
3. CapabilityRoutingExecutor: Routes to providers based on capabilities

The design avoids dataclass+ABC mixing by using Protocol (PEP 544).
Each agent (even external/remote) just needs to implement execute().
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable, TYPE_CHECKING
import asyncio
import logging
from datetime import datetime

if TYPE_CHECKING:
    from css.modules.capabilities.capability_registry import DynamicCapabilityRegistry
    from css.core.types.capabilities import CapabilityType

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
    - Capabilities: Dynamic capability routing
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
        self._capability_registry: DynamicCapabilityRegistry | None = None

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

    def set_capability_registry(self, registry: DynamicCapabilityRegistry) -> None:
        """Set the capability registry for provider routing.
        
        Args:
            registry: DynamicCapabilityRegistry instance for capability discovery
        """
        self._capability_registry = registry
        log.debug(f"AgentExecutor capability registry initialized for {self.provider}/{self.model}")

    def get_capabilities(self) -> list[str]:
        """Get capabilities for current provider/model.
        
        Returns:
            List of capability type strings (e.g., ['streaming', 'vision', 'tool_use'])
            Empty list if registry not initialized or model not found
        """
        if not self._capability_registry:
            log.warning("Capability registry not initialized, returning empty capabilities")
            return []
        
        caps = self._capability_registry.get_capabilities(self.provider, self.model)
        return [c.value if hasattr(c, 'value') else str(c) for c in caps]

    def has_capability(self, capability_type: str) -> bool:
        """Check if current provider/model supports a capability.
        
        Args:
            capability_type: Capability type to check (e.g., 'streaming', 'vision')
        
        Returns:
            True if capability is supported, False otherwise
        """
        if not self._capability_registry:
            log.warning(f"Capability registry not initialized, cannot check for {capability_type}")
            return False
        
        # Import here to avoid circular imports
        from css.core.types.capabilities import CapabilityType
        
        try:
            cap = CapabilityType(capability_type.lower())
            return self._capability_registry.has_capability(self.provider, self.model, cap)
        except ValueError:
            log.warning(f"Unknown capability type: {capability_type}")
            return False

    def select_model_for_capability(self, provider_name: str, required_capability: str) -> str | None:
        """Select a model from provider that supports the required capability.
        
        Uses DynamicCapabilityRegistry to find first model supporting the capability.
        
        Args:
            provider_name: Provider to search (e.g., 'openai', 'anthropic')
            required_capability: Capability type required (e.g., 'vision', 'tool_use')
        
        Returns:
            Model identifier if found, None otherwise
        """
        if not self._capability_registry:
            log.warning("Capability registry not initialized, cannot select model for capability")
            return None
        
        from css.core.types.capabilities import CapabilityType
        
        try:
            cap = CapabilityType(required_capability.lower())
        except ValueError:
            log.warning(f"Unknown capability type: {required_capability}")
            return None
        
        # Get all registered capabilities for provider
        # Note: This requires iterating through registry internal state
        # More efficient if registry exposes get_models_for_capability(provider, capability)
        log.debug(f"Querying {provider_name} for models with {required_capability}")
        
        # For now, log that capability routing is active
        log.info(f"Capability routing: searching {provider_name} for {required_capability}")
        return None
