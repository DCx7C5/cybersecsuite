"""Capability types for LLM models and providers.

Defines what features each model supports (streaming, vision, tools, etc.)
and how to discover/register capabilities at runtime.
"""

from datetime import datetime, timedelta, timezone

import msgspec

from css.core.types.base_enums import CapabilityType, MemorySupportMode


class Capability(msgspec.Struct, frozen=True, kw_only=True):
    """Single capability supported by a model."""

    name: str
    type: CapabilityType
    supported: bool = True
    version: str = "0.1.0"
    notes: str | None = None
    cost_multiplier: float | int = 1.0
    metadata: dict[str, object] = msgspec.field(default_factory=dict)


class ModelCapabilities(msgspec.Struct, frozen=True, kw_only=True):
    """Complete capability set for a single model."""

    provider: str
    model_name: str
    max_tokens: int
    context_window: int
    estimated_cost_per_1k_tokens: float | int
    latency_ms: float | int
    memory_support_mode: MemorySupportMode = MemorySupportMode.PLATFORM_EMULATED
    discovered_at: datetime = msgspec.field(default_factory=lambda: datetime.now(timezone.utc))
    capabilities: list[Capability] = msgspec.field(default_factory=list)
    cache_ttl: timedelta = timedelta(hours=24)

    def has_capability(self, capability_type: CapabilityType) -> bool:
        """Check if model supports a capability."""
        return any(c.type == capability_type and c.supported for c in self.capabilities)

    def get_capability(self, capability_type: CapabilityType) -> Capability | None:
        """Get capability details if supported."""
        for c in self.capabilities:
            if c.type == capability_type and c.supported:
                return c
        return None


class CapabilityRegistry(msgspec.Struct, kw_only=True):
    """Registry of capabilities for all providers/models.

    Used to discover what features each model supports, enabling dynamic
    routing and orchestration decisions.
    """

    capabilities: dict[str, ModelCapabilities] = msgspec.field(default_factory=dict)
    last_sync: datetime = msgspec.field(default_factory=lambda: datetime.now(timezone.utc))
    cache_ttl: timedelta = timedelta(hours=24)

    def register_capability(self, model_caps: ModelCapabilities) -> None:
        """Register capabilities for a model."""
        key = f"{model_caps.provider}:{model_caps.model_name}"
        self.capabilities[key] = model_caps

    def get_capabilities(self, provider: str, model_name: str) -> ModelCapabilities | None:
        """Get capabilities for specific model."""
        key = f"{provider}:{model_name}"
        return self.capabilities.get(key)

    def get_capabilities_by_type(self, capability_type: CapabilityType) -> list[ModelCapabilities]:
        """Get all models supporting a specific capability."""
        result = []
        for caps in self.capabilities.values():
            if caps.has_capability(capability_type):
                result.append(caps)
        return result

    def is_cache_stale(self) -> bool:
        """Check if capabilities cache needs refresh."""
        elapsed = datetime.now(timezone.utc) - self.last_sync
        return elapsed > self.cache_ttl

    def needs_discovery(self, provider: str) -> bool:
        """Check if we need to discover capabilities for this provider.

        Returns True if:
        - Provider not in registry, OR
        - Cache is stale
        """
        has_provider = any(key.startswith(f"{provider}:") for key in self.capabilities.keys())
        return not has_provider or self.is_cache_stale()
