"""Capability types for LLM models and providers.

Defines what features each model supports (streaming, vision, tools, etc.)
and how to discover/register capabilities at runtime.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional
from datetime import datetime, timedelta

from pydantic import BaseModel, Field


class CapabilityType(str, Enum):
    """11 capability types supported across LLM providers."""

    STREAMING = "streaming"  # Text generation streaming
    VISION = "vision"  # Image input processing
    TOOL_USE = "tool_use"  # Function calling / tools use
    VISION_AND_TOOL = "vision_and_tool"  # Combined vision + tools
    JSON_MODE = "json_mode"  # Structured JSON output
    LONG_CONTEXT = "long_context"  # Extended context windows (32k+)
    BATCH_PROCESSING = "batch_processing"  # Batch API support
    EMBEDDINGS = "embeddings"  # Text embeddings
    RETRIEVAL = "retrieval"  # RAG / knowledge base retrieval
    FINE_TUNING = "fine_tuning"  # Model fine-tuning support
    REASONING = "reasoning"  # Extended reasoning (o1-style)


@dataclass
class Capability(BaseModel):
    """Single capability supported by a model."""

    name: str = Field(..., description="Capability name (e.g., 'streaming', 'vision')")
    type: CapabilityType = Field(..., description="Capability type")
    supported: bool = Field(default=True, description="Is this capability supported?")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extra capability details")
    version: str = Field(default="1.0", description="Capability API version")
    cost_multiplier: float = Field(default=1.0, description="Cost impact of using this capability")
    notes: Optional[str] = Field(default=None, description="Human-readable notes about capability")

    class Config:
        """Pydantic config."""

        use_enum_values = False


@dataclass
class ModelCapabilities(BaseModel):
    """Complete capability set for a single model."""

    provider: str = Field(..., description="Provider name (e.g., 'openai', 'anthropic')")
    model_name: str = Field(..., description="Model identifier (e.g., 'gpt-4', 'claude-3-sonnet')")
    capabilities: list[Capability] = Field(default_factory=list, description="List of supported capabilities")
    max_tokens: int = Field(default=4000, description="Max tokens in single request")
    context_window: int = Field(default=4000, description="Total context window size")
    estimated_cost_per_1k_tokens: float = Field(default=0.0, description="Cost per 1k tokens")
    latency_ms: float = Field(default=0.0, description="Estimated latency in milliseconds")
    discovered_at: datetime = Field(default_factory=datetime.utcnow, description="When capabilities were discovered")
    cache_ttl: timedelta = Field(default=timedelta(hours=24), description="How long to cache these capabilities")

    class Config:
        """Pydantic config."""

        use_enum_values = False

    def has_capability(self, capability_type: CapabilityType) -> bool:
        """Check if model supports a capability."""
        return any(
            c.type == capability_type and c.supported
            for c in self.capabilities
        )

    def get_capability(self, capability_type: CapabilityType) -> Optional[Capability]:
        """Get capability details if supported."""
        for c in self.capabilities:
            if c.type == capability_type and c.supported:
                return c
        return None


@dataclass
class CapabilityRegistry(BaseModel):
    """Registry of capabilities for all providers/models.

    Used to discover what features each model supports, enabling dynamic
    routing and orchestration decisions.
    """

    capabilities: dict[str, ModelCapabilities] = Field(
        default_factory=dict,
        description="Key: '{provider}:{model_name}', Value: ModelCapabilities",
    )
    last_sync: datetime = Field(default_factory=datetime.utcnow, description="Last time capabilities were synced")
    cache_ttl: timedelta = Field(default=timedelta(hours=24), description="How long to cache registry")

    class Config:
        """Pydantic config."""

        use_enum_values = False

    def register_capability(self, model_caps: ModelCapabilities) -> None:
        """Register capabilities for a model."""
        key = f"{model_caps.provider}:{model_caps.model_name}"
        self.capabilities[key] = model_caps

    def get_capabilities(self, provider: str, model_name: str) -> Optional[ModelCapabilities]:
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
        elapsed = datetime.utcnow() - self.last_sync
        return elapsed > self.cache_ttl

    def needs_discovery(self, provider: str) -> bool:
        """Check if we need to discover capabilities for this provider.

        Returns True if:
        - Provider not in registry, OR
        - Cache is stale
        """
        has_provider = any(
            key.startswith(f"{provider}:")
            for key in self.capabilities.keys()
        )
        return not has_provider or self.is_cache_stale()


# Preset capability sets for common models

DEFAULT_CAPABILITIES: dict[str, list[CapabilityType]] = {
    "gpt-4": [
        CapabilityType.STREAMING,
        CapabilityType.VISION,
        CapabilityType.TOOL_USE,
        CapabilityType.VISION_AND_TOOL,
        CapabilityType.JSON_MODE,
        CapabilityType.LONG_CONTEXT,
    ],
    "claude-3-sonnet": [
        CapabilityType.STREAMING,
        CapabilityType.VISION,
        CapabilityType.TOOL_USE,
        CapabilityType.VISION_AND_TOOL,
        CapabilityType.JSON_MODE,
        CapabilityType.LONG_CONTEXT,
    ],
    "gpt-3.5-turbo": [
        CapabilityType.STREAMING,
        CapabilityType.TOOL_USE,
        CapabilityType.JSON_MODE,
    ],
    "ollama": [
        CapabilityType.STREAMING,
        CapabilityType.EMBEDDINGS,
    ],
}
