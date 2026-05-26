"""LLM model registry — tracks available models and their capabilities.

The registry is the single source of truth for what providers/models are
known to the system.  It is populated at startup by ``seed-providers``
(T5.2).  In Phase 5 it holds a hardcoded ``DEFAULT_MODELS`` dict built from
the api_services/ directory so that HybridTool provider validation works
without a running database.

Phase 16: Dynamic model discovery support — providers can populate the
registry asynchronously via discover_models() protocol. Seeds remain as
static fallback for startup bootstrap.
"""

import pkgutil
from pathlib import Path
from typing import Callable, Any
import time

from css.core.types.meta import AsyncSafeSingletonMeta

from .models import ModelMetadata
from .enums import ModelCapability


def _known_provider_ids() -> set[str]:
    """Return the set of provider slug strings present under api_services/."""
    api_services = Path(__file__).resolve().parents[2] / "api_services"
    return {
        name
        for _, name, is_pkg in pkgutil.iter_modules([str(api_services)])
        if is_pkg and not name.startswith("_")
    }


# Built from api_services/ directory discovery — same slugs used as ProviderType
# values and as HybridToolSchema.fallback_provider identifiers.
_KNOWN_PROVIDERS: set[str] = _known_provider_ids()

# Phase 16 T16.A-3: Seed thinking-capable models (Anthropic, OpenAI, DeepSeek)
# Full records are inserted by ``seed-providers`` (T5.2).
try:
    from .seeds import DEFAULT_MODELS_THINKING
    DEFAULT_MODELS: dict[str, ModelMetadata] = dict(DEFAULT_MODELS_THINKING)
except (ImportError, Exception):
    # Fallback if seeds cannot be imported
    DEFAULT_MODELS = {}


class ModelRegistry(metaclass=AsyncSafeSingletonMeta):
    """In-memory registry mapping model IDs to ModelMetadata.

    Uses AsyncSafeSingletonMeta for async-safe singleton pattern.
    Acts as both a lookup table (get_model) and a provider validator
    (is_known_provider).  The latter is used by ToolRegistry to validate
    HybridToolSchema.fallback_provider before registration.
    
    Phase 16: Supports dynamic model discovery via async provider callbacks.
    Each provider can register a discovery function that populates new models
    at runtime. Cache TTL prevents excessive re-fetching.
    """

    def __init__(self) -> None:
        self._models: dict[str, ModelMetadata] = dict(DEFAULT_MODELS)
        # Dynamic discovery: provider slug → (async callable, last_fetch_ts, ttl_seconds)
        self._discovery_funcs: dict[str, tuple[Callable[[], Any], float, int]] = {}
        # Cache: provider → list of model IDs discovered
        self._discovered_cache: dict[str, list[str]] = {}

    def register(self, model: ModelMetadata) -> None:
        """Add or replace *model* in the registry."""
        self._models[model.id] = model

    def register_many(self, models: list[ModelMetadata]) -> None:
        """Bulk-register a list of models."""
        for model in models:
            self.register(model)

    def get_model(self, model_id: str) -> ModelMetadata | None:
        """Return the ModelMetadata for *model_id*, or None."""
        return self._models.get(model_id)

    def list_models(
        self,
        provider: str | None = None,
        capability: ModelCapability | None = None,
    ) -> list[ModelMetadata]:
        """Return all registered models, optionally filtered."""
        result = list(self._models.values())
        if provider:
            result = [m for m in result if str(m.provider.value) == provider]
        if capability:
            result = [m for m in result if m.supports_capability(capability)]
        return result

    def supports_capability(self, model_id: str, capability: ModelCapability) -> bool:
        """Check if a specific model supports a capability."""
        model = self.get_model(model_id)
        if not model:
            return False
        return model.supports_capability(capability)

    def thinking_capable_models(self, provider: str | None = None) -> list[ModelMetadata]:
        """Return all models that support extended thinking, optionally filtered by provider."""
        return self.list_models(
            provider=provider,
            capability=ModelCapability.EXTENDED_THINKING,
        )

    def can_think(self, model_id: str) -> bool:
        """Convenience method: does this model support extended thinking?"""
        return self.supports_capability(model_id, ModelCapability.EXTENDED_THINKING)

    def register_discovery(
        self,
        provider: str,
        discovery_func: Callable[[], Any],
        ttl_seconds: int = 3600,
    ) -> None:
        """Register an async discovery function for a provider.
        
        Args:
            provider: Provider slug (e.g., 'openrouter', 'xai')
            discovery_func: Async callable that returns list[ModelMetadata]
            ttl_seconds: Cache TTL in seconds (default 1 hour)
        """
        self._discovery_funcs[provider] = (discovery_func, 0.0, ttl_seconds)

    async def discover_models(self, provider: str) -> list[ModelMetadata]:
        """Fetch models from a provider's discovery function.
        
        Uses cache with TTL to avoid excessive re-fetching.
        Returns empty list if provider not registered or discovery fails.
        """
        if provider not in self._discovery_funcs:
            return []

        discovery_func, last_fetch, ttl = self._discovery_funcs[provider]
        now = time.time()

        # Check if cache is still valid
        if now - last_fetch < ttl and provider in self._discovered_cache:
            model_ids = self._discovered_cache.get(provider, [])
            return [m for m in self._models.values() if m.id in model_ids]

        # Fetch fresh models
        try:
            models = await discovery_func()
            if models:
                # Register all discovered models
                self.register_many(models)
                # Cache model IDs for this provider
                model_ids = [m.id for m in models]
                self._discovered_cache[provider] = model_ids
                # Update fetch timestamp
                self._discovery_funcs[provider] = (discovery_func, now, ttl)
                return models
        except Exception:
            # Discovery failed; fall back to cached if available
            if provider in self._discovered_cache:
                model_ids = self._discovered_cache[provider]
                return [m for m in self._models.values() if m.id in model_ids]
        return []

    def models_by_provider(self, provider: str) -> list[ModelMetadata]:
        """Get all models for a provider (both seeded and discovered)."""
        return [m for m in self._models.values() if str(m.provider.value) == provider]

    def is_known_provider(self, provider_slug: str) -> bool:
        """Return True if *provider_slug* exists in api_services/.

        Filesystem-based check — works even before models are seeded.
        """
        return provider_slug in _KNOWN_PROVIDERS

    def known_providers(self) -> set[str]:
        """Return the full set of known provider slugs."""
        return set(_KNOWN_PROVIDERS)

    def __len__(self) -> int:
        return len(self._models)


def get_model_registry() -> "ModelRegistry":
    """Return the global ModelRegistry singleton."""
    return ModelRegistry()  # type: ignore[return-value]


__all__ = ["ModelRegistry", "DEFAULT_MODELS", "get_model_registry"]
