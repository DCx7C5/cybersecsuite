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


# ===== SEED DATA: Thinking-Capable Models (Phase 16 T16.A-3) =====

# Anthropic: Extended thinking models (budget_tokens)
ANTHROPIC_MODELS = [
    _mk(
        "claude-3-7-sonnet-20250219",
        "anthropic",
        "Claude 3.7 Sonnet",
        ModelFamily.SONNET,
        context_window=200000,
        max_output_tokens=16000,
        latency_ms=3000,
        capabilities=_cap("streaming", "tool_use", "function_calling", "extended_thinking", "vision"),
        pricing=ModelPricing(
            input_tokens_per_1k=0.003,
            output_tokens_per_1k=0.015,
        ),
    ),
    _mk(
        "claude-3-7-opus-20250219",
        "anthropic",
        "Claude 3.7 Opus",
        ModelFamily.OPUS,
        context_window=200000,
        max_output_tokens=16000,
        latency_ms=5000,
        capabilities=_cap("streaming", "tool_use", "function_calling", "extended_thinking", "vision"),
        pricing=ModelPricing(
            input_tokens_per_1k=0.015,
            output_tokens_per_1k=0.075,
        ),
    ),
]

# OpenAI: Reasoning models (reasoning_effort)
OPENAI_MODELS = [
    _mk(
        "gpt-4o",
        "openai",
        "GPT-4o",
        ModelFamily.GPT,
        context_window=128000,
        max_output_tokens=4096,
        latency_ms=2000,
        capabilities=_cap("streaming", "tool_use", "function_calling", "vision", "json_mode"),
        pricing=ModelPricing(
            input_tokens_per_1k=0.005,
            output_tokens_per_1k=0.015,
        ),
    ),
    _mk(
        "o1",
        "openai",
        "GPT-o1",
        ModelFamily.GPT,
        context_window=128000,
        max_output_tokens=32768,
        latency_ms=30000,
        capabilities=_cap("extended_thinking", "tool_use"),
        pricing=ModelPricing(
            input_tokens_per_1k=0.015,
            output_tokens_per_1k=0.060,
        ),
    ),
    _mk(
        "o3",
        "openai",
        "GPT-o3",
        ModelFamily.GPT,
        context_window=128000,
        max_output_tokens=32768,
        latency_ms=60000,
        capabilities=_cap("extended_thinking", "tool_use"),
        pricing=ModelPricing(
            input_tokens_per_1k=0.020,
            output_tokens_per_1k=0.080,
        ),
    ),
]

# DeepSeek: Reasoning models (thinking capability)
DEEPSEEK_MODELS = [
    _mk(
        "deepseek-reasoner",
        "deepseek",
        "DeepSeek Reasoner",
        ModelFamily.DEEPSEEK_MODEL,
        context_window=64000,
        max_output_tokens=8000,
        latency_ms=15000,
        capabilities=_cap("streaming", "extended_thinking", "tool_use"),
        pricing=ModelPricing(
            input_tokens_per_1k=0.00055,
            output_tokens_per_1k=0.00219,
        ),
    ),
]

# Combine all thinking-capable seeds
DEFAULT_MODELS_THINKING = {
    m.id: m for m in ANTHROPIC_MODELS + OPENAI_MODELS + DEEPSEEK_MODELS
}

