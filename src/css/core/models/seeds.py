"""Provider model seed data for Phase 5.

Populates DEFAULT_MODELS in the ModelRegistry with representative models
for each of the 24 api_services providers.  Full introspection (calling
each provider's get_models() API) is deferred to Phase 3.

This module is imported by registry.py to set DEFAULT_MODELS.
"""


from .models import ModelMetadata, ModelPricing
from .enums import ModelFamily, ModelCapability


def _cap(*caps: str) -> set[ModelCapability]:
    """Helper to build a capability set from string names."""
    return {ModelCapability(c) for c in caps}


def _mk(
    model_id: str,
    provider_slug: str,
    display_name: str,
    family: ModelFamily,
    context_window: int,
    max_output_tokens: int,
    latency_ms: int = 2000,
    capabilities: set[ModelCapability] | None = None,
    pricing: ModelPricing | None = None,
) -> ModelMetadata:
    """Create a ModelMetadata with a dynamic ModelProvider lookup."""
    from .enums import ModelProvider

    # ModelProvider is dynamically generated from api_services/ directories.
    # Attribute name is the upper-cased slug.
    prov = getattr(ModelProvider, provider_slug.upper(), None)
    if prov is None:
        # Fallback: iterate to find by value
        for member in ModelProvider:
            if member.value == provider_slug:
                prov = member
                break
    if prov is None:
        raise ValueError(f"ModelProvider not found for slug: {provider_slug}")

    return ModelMetadata(
        id=model_id,
        provider=prov,
        family=family,
        display_name=display_name,
        context_window=context_window,
        max_output_tokens=max_output_tokens,
        latency_ms=latency_ms,
        capabilities=capabilities or _cap("streaming", "tool_use", "function_calling"),
        pricing=pricing,
    )

