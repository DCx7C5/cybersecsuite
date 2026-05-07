"""LLM model registry — tracks available models and their capabilities.

The registry is the single source of truth for what providers/models are
known to the system.  It is populated at startup by ``seed-providers``
(T5.2).  In Phase 5 it holds a hardcoded ``DEFAULT_MODELS`` dict built from
the api_services/ directory so that HybridTool provider validation works
without a running database.
"""


import pkgutil
from pathlib import Path

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

# Minimal stub records so the registry is non-empty in Phase 5 without seeding.
# Full records are inserted by ``seed-providers`` (T5.2).
DEFAULT_MODELS: dict[str, ModelMetadata] = {}


class ModelRegistry:
    """In-memory registry mapping model IDs to ModelMetadata.

    Acts as both a lookup table (get_model) and a provider validator
    (is_known_provider).  The latter is used by ToolRegistry to validate
    HybridToolSchema.fallback_provider before registration.
    """

    def __init__(self) -> None:
        self._models: dict[str, ModelMetadata] = dict(DEFAULT_MODELS)

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


# Module-level singleton
_model_registry: ModelRegistry | None = None


def get_model_registry() -> ModelRegistry:
    """Return the global ModelRegistry singleton."""
    global _model_registry
    if _model_registry is None:
        _model_registry = ModelRegistry()
    return _model_registry


__all__ = ["ModelRegistry", "DEFAULT_MODELS", "get_model_registry"]
