"""Base agent protocol and executor — minimal Protocol for agent execution.

This module defines:
1. BaseAgent Protocol: Minimal interface for agent-like systems
2. AgentExecutor: Runs an agent with an LLM provider via HttpProviderAdapter
3. AgentResult: Structured result (msgspec.Struct for Phase 6 P1)

The design uses Protocol (PEP 544) and wires to ProviderRegistry + HttpProviderAdapter.
Replaces Claude SDK hardcode with provider-agnostic execution.
"""

from typing import Protocol, runtime_checkable, TYPE_CHECKING
import logging
from datetime import datetime

import msgspec

if TYPE_CHECKING:
    from css.modules.capabilities.capability_registry import DynamicCapabilityRegistry

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
    ) -> "AgentResult":
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


class AgentResult(msgspec.Struct, frozen=True):
    """Structured result from agent execution (msgspec.Struct for Phase 6 P1).
    
    Attributes:
        response: Final agent response (text)
        thinking: Internal reasoning chain (if available)
        tool_calls: Any tools the agent tried to use
        stop_reason: Why execution stopped (end_turn, tool_use, max_tokens, etc.)
        input_tokens: Token count for prompt
        output_tokens: Token count for response
        duration_ms: Execution time in milliseconds
        executed_at: Timestamp of execution (ISO format string)
        provider: Which LLM provider was used
        model: Which model variant
    """
    
    response: str = ""
    thinking: str | None = None
    tool_calls: list[dict] = msgspec.field(default_factory=list)
    stop_reason: str = "end_turn"
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: float = 0.0
    executed_at: str = ""
    provider: str = "unknown"
    model: str = "unknown"
    
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
            "executed_at": self.executed_at,
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
    """Executes agent prompts via ProviderRegistry + HttpProviderAdapter.
    
    Wires together:
    - AgentExecutor.execute() → DynamicCapabilityRegistry.select_provider()
    - → HttpProviderAdapter.complete()
    - → AgentResult
    
    No more Claude SDK hardcode — agents become provider-agnostic.
    """
    
    def __init__(self, provider: str, model: str):
        """Initialize executor with provider/adapter (not raw client).
        
        Args:
            provider: Provider name (openai, anthropic, ollama, etc.)
            model: Model identifier (gpt-4, claude-3-opus, etc.)
        """
        self.provider = provider
        self.model = model
        self._capability_registry: DynamicCapabilityRegistry | None = None
        self._adapter = None
    
    async def _get_adapter(self):
        """Lazily get HttpProviderAdapter from ProviderRegistry."""
        if self._adapter is None:
            from css.api_services.registry import get_registry
            registry = get_registry()
            self._adapter = registry.get_provider(self.provider)
        return self._adapter
    
    async def execute(
        self,
        prompt: str,
        context: dict | None = None,
        system: str | None = None,
        **kwargs,
    ) -> AgentResult:
        """Execute agent prompt via provider-agnostic adapter.
        
        Args:
            prompt: User prompt
            context: Optional conversation context (for future multi-turn)
            system: Optional system message
            **kwargs: Provider-specific options (temperature, max_tokens, etc.)
            
        Returns:
            AgentResult with response and metadata
        """
        import time
        
        adapter = await self._get_adapter()
        
        start = time.time()
        try:
            result_dict = await adapter.complete(
                prompt=prompt,
                model=self.model,
                system=system,
                **kwargs,
            )
        except Exception as e:
            log.error(f"AgentExecutor: Provider {self.provider}/{self.model} failed: {e}")
            raise
        
        duration_ms = (time.time() - start) * 1000
        
        # Build AgentResult from adapter response
        return AgentResult(
            response=result_dict.get("response", ""),
            stop_reason=result_dict.get("stop_reason", "unknown"),
            input_tokens=result_dict.get("input_tokens", 0),
            output_tokens=result_dict.get("output_tokens", 0),
            duration_ms=duration_ms,
            executed_at=datetime.now().isoformat(),
            provider=self.provider,
            model=self.model,
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
    
    async def select_provider_for_capability(
        self, required_capability: str
    ) -> str | None:
        """Select best provider/model for a required capability.
        
        Uses DynamicCapabilityRegistry to find capable providers.
        Updates self.provider and self.model if successful.
        
        Args:
            required_capability: Capability needed (e.g., 'vision', 'tool_use')
            
        Returns:
            Model identifier if found, None otherwise
            
        Side Effects:
            Updates self.provider and self.model on success
        """
        if not self._capability_registry:
            log.warning("Capability registry not initialized, cannot select provider")
            return None
        
        from css.core.types.capabilities import CapabilityType
        
        try:
            cap = CapabilityType(required_capability.lower())
        except ValueError:
            log.warning(f"Unknown capability type: {required_capability}")
            return None
        
        # Get all providers from registry
        from css.api_services.registry import get_registry
        registry = get_registry()
        providers = registry.list_providers()
        
        for provider_name in providers:
            models = registry.get_spec(provider_name)
            if models is None:
                continue
            
            # Check if any model supports this capability
            for model_id in models.models:
                if self._capability_registry.has_capability(
                    provider_name, model_id, cap
                ):
                    # Found a match
                    log.info(
                        f"Capability routing: {required_capability} → "
                        f"{provider_name}/{model_id}"
                    )
                    self.provider = provider_name
                    self.model = model_id
                    self._adapter = None  # Force re-init with new provider
                    return model_id
        
        log.warning(f"No provider found for capability: {required_capability}")
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
