"""Provider model seed data for Phase 5.

Populates DEFAULT_MODELS in the ModelRegistry with representative models
for each of the 24 api_services providers.  Full introspection (calling
each provider's get_models() API) is deferred to Phase 3.

This module is imported by registry.py to set DEFAULT_MODELS.
"""

from __future__ import annotations

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


# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------
ANTHROPIC_MODELS = [
    _mk("claude-3-5-sonnet-20241022", "anthropic", "Claude 3.5 Sonnet", ModelFamily.SONNET,
        200_000, 16_384, 1500, _cap("streaming", "vision", "tool_use", "function_calling", "long_context", "json_mode"),
        ModelPricing(3.0, 15.0)),
    _mk("claude-3-opus-20250219", "anthropic", "Claude 3 Opus", ModelFamily.OPUS,
        200_000, 4_096, 4000, _cap("streaming", "vision", "tool_use", "function_calling", "long_context", "extended_thinking"),
        ModelPricing(15.0, 75.0)),
    _mk("claude-3-haiku-20240307", "anthropic", "Claude 3 Haiku", ModelFamily.HAIKU,
        200_000, 4_096, 500, _cap("streaming", "vision", "tool_use", "function_calling", "long_context"),
        ModelPricing(0.25, 1.25)),
]

# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------
OPENAI_MODELS = [
    _mk("gpt-4o", "openai", "GPT-4o", ModelFamily.GPT,
        128_000, 16_384, 2000, _cap("streaming", "vision", "tool_use", "function_calling", "json_mode"),
        ModelPricing(2.5, 10.0)),
    _mk("gpt-4o-mini", "openai", "GPT-4o Mini", ModelFamily.GPT,
        128_000, 16_384, 800, _cap("streaming", "vision", "tool_use", "function_calling", "json_mode"),
        ModelPricing(0.15, 0.60)),
    _mk("o3-mini", "openai", "o3-mini", ModelFamily.GPT,
        200_000, 100_000, 10_000, _cap("streaming", "tool_use", "function_calling", "extended_thinking", "long_context"),
        ModelPricing(1.1, 4.4)),
]

# ---------------------------------------------------------------------------
# Google Gemini
# ---------------------------------------------------------------------------
GEMINI_MODELS = [
    _mk("gemini-2.0-flash", "gemini", "Gemini 2.0 Flash", ModelFamily.GEMINI,
        1_048_576, 8_192, 800, _cap("streaming", "vision", "tool_use", "function_calling", "long_context", "json_mode"),
        ModelPricing(0.10, 0.40)),
    _mk("gemini-2.5-pro", "gemini", "Gemini 2.5 Pro", ModelFamily.GEMINI,
        1_048_576, 65_536, 3000, _cap("streaming", "vision", "tool_use", "function_calling", "long_context", "extended_thinking"),
        ModelPricing(1.25, 10.0)),
]

# ---------------------------------------------------------------------------
# DeepSeek
# ---------------------------------------------------------------------------
DEEPSEEK_MODELS = [
    _mk("deepseek-chat", "deepseek", "DeepSeek Chat (V3)", ModelFamily.DEEPSEEK_MODEL,
        64_000, 8_192, 2500, _cap("streaming", "tool_use", "function_calling", "json_mode"),
        ModelPricing(0.27, 1.10)),
    _mk("deepseek-reasoner", "deepseek", "DeepSeek R1", ModelFamily.DEEPSEEK_MODEL,
        64_000, 8_192, 5000, _cap("streaming", "extended_thinking"),
        ModelPricing(0.55, 2.19)),
]

# ---------------------------------------------------------------------------
# Groq
# ---------------------------------------------------------------------------
GROQ_MODELS = [
    _mk("llama-3.3-70b-versatile", "groq", "Llama 3.3 70B (Groq)", ModelFamily.LLAMA,
        128_000, 32_768, 200, _cap("streaming", "tool_use", "function_calling", "json_mode"),
        ModelPricing(0.59, 0.79)),
    _mk("llama-3.1-8b-instant", "groq", "Llama 3.1 8B Instant (Groq)", ModelFamily.LLAMA,
        128_000, 8_192, 80, _cap("streaming", "tool_use"),
        ModelPricing(0.05, 0.08)),
]

# ---------------------------------------------------------------------------
# Mistral
# ---------------------------------------------------------------------------
MISTRAL_MODELS = [
    _mk("mistral-large-latest", "mistral", "Mistral Large", ModelFamily.MISTRAL_MODEL,
        128_000, 8_192, 2000, _cap("streaming", "tool_use", "function_calling", "json_mode"),
        ModelPricing(2.0, 6.0)),
    _mk("mistral-small-latest", "mistral", "Mistral Small", ModelFamily.MISTRAL_MODEL,
        32_000, 8_192, 800, _cap("streaming", "tool_use", "function_calling"),
        ModelPricing(0.1, 0.3)),
]

# ---------------------------------------------------------------------------
# xAI
# ---------------------------------------------------------------------------
XAI_MODELS = [
    _mk("grok-3", "xai", "Grok 3", ModelFamily.OPEN_SOURCE,
        131_072, 32_768, 2000, _cap("streaming", "tool_use", "function_calling", "vision"),
        ModelPricing(3.0, 15.0)),
]

# ---------------------------------------------------------------------------
# NVIDIA
# ---------------------------------------------------------------------------
NVIDIA_MODELS = [
    _mk("meta/llama-3.3-70b-instruct", "nvidia", "Llama 3.3 70B (NVIDIA)", ModelFamily.LLAMA,
        128_000, 4_096, 1500, _cap("streaming", "tool_use", "function_calling"),
        ModelPricing(0.23, 0.40)),
]

# ---------------------------------------------------------------------------
# Cerebras
# ---------------------------------------------------------------------------
CEREBRAS_MODELS = [
    _mk("llama-3.3-70b", "cerebras", "Llama 3.3 70B (Cerebras)", ModelFamily.LLAMA,
        128_000, 8_192, 150, _cap("streaming", "tool_use", "function_calling"),
        ModelPricing(0.60, 0.60)),
    _mk("qwen-3-32b", "cerebras", "Qwen 3 32B (Cerebras)", ModelFamily.OPEN_SOURCE,
        128_000, 8_192, 120, _cap("streaming", "tool_use", "function_calling"),
        ModelPricing(0.40, 0.40)),
]

# ---------------------------------------------------------------------------
# SambaNova
# ---------------------------------------------------------------------------
SAMBANOVA_MODELS = [
    _mk("Meta-Llama-3.3-70B-Instruct", "sambanova", "Llama 3.3 70B (SambaNova)", ModelFamily.LLAMA,
        128_000, 16_384, 300, _cap("streaming", "tool_use"),
        ModelPricing(0.60, 1.20)),
]

# ---------------------------------------------------------------------------
# Together AI
# ---------------------------------------------------------------------------
TOGETHER_MODELS = [
    _mk("meta-llama/Llama-3.3-70B-Instruct-Turbo", "together", "Llama 3.3 70B Turbo (Together)", ModelFamily.LLAMA,
        128_000, 4_096, 1000, _cap("streaming", "tool_use", "function_calling"),
        ModelPricing(0.88, 0.88)),
]

# ---------------------------------------------------------------------------
# OpenRouter (routing only — expose a representative meta-model)
# ---------------------------------------------------------------------------
OPENROUTER_MODELS = [
    _mk("openrouter/auto", "openrouter", "OpenRouter Auto", ModelFamily.OPEN_SOURCE,
        200_000, 32_768, 2000, _cap("streaming", "tool_use", "function_calling"),
        None),
]

# ---------------------------------------------------------------------------
# Cloudflare Workers AI
# ---------------------------------------------------------------------------
CLOUDFLARE_MODELS = [
    _mk("@cf/meta/llama-3.1-8b-instruct", "cloudflare", "Llama 3.1 8B (Cloudflare)", ModelFamily.LLAMA,
        128_000, 4_096, 600, _cap("streaming"),
        ModelPricing(0.0, 0.0)),  # Free tier
]

# ---------------------------------------------------------------------------
# Perplexity
# ---------------------------------------------------------------------------
PERPLEXITY_MODELS = [
    _mk("sonar-pro", "perplexity", "Sonar Pro", ModelFamily.OPEN_SOURCE,
        200_000, 8_000, 3000, _cap("streaming", "tool_use"),
        ModelPricing(3.0, 15.0)),
]

# ---------------------------------------------------------------------------
# Cohere
# ---------------------------------------------------------------------------
COHERE_MODELS = [
    _mk("command-r-plus-08-2024", "cohere", "Command R+ (Cohere)", ModelFamily.OPEN_SOURCE,
        128_000, 4_096, 2000, _cap("streaming", "tool_use", "function_calling"),
        ModelPricing(2.5, 10.0)),
]

# ---------------------------------------------------------------------------
# AI21
# ---------------------------------------------------------------------------
AI21_MODELS = [
    _mk("jamba-1.5-large", "ai21", "Jamba 1.5 Large (AI21)", ModelFamily.OPEN_SOURCE,
        256_000, 4_096, 2000, _cap("streaming", "tool_use", "function_calling"),
        ModelPricing(2.0, 8.0)),
]

# ---------------------------------------------------------------------------
# Fireworks
# ---------------------------------------------------------------------------
FIREWORKS_MODELS = [
    _mk("accounts/fireworks/models/llama-v3p3-70b-instruct", "fireworks",
        "Llama 3.3 70B (Fireworks)", ModelFamily.LLAMA,
        128_000, 16_384, 800, _cap("streaming", "tool_use", "function_calling"),
        ModelPricing(0.90, 0.90)),
]

# ---------------------------------------------------------------------------
# DeepInfra
# ---------------------------------------------------------------------------
DEEPINFRA_MODELS = [
    _mk("meta-llama/Llama-3.3-70B-Instruct", "deepinfra", "Llama 3.3 70B (DeepInfra)", ModelFamily.LLAMA,
        128_000, 4_096, 900, _cap("streaming", "tool_use", "function_calling"),
        ModelPricing(0.23, 0.40)),
]

# ---------------------------------------------------------------------------
# HuggingFace
# ---------------------------------------------------------------------------
HUGGINGFACE_MODELS = [
    _mk("meta-llama/Llama-3.3-70B-Instruct", "huggingface", "Llama 3.3 70B (HuggingFace Inference)", ModelFamily.LLAMA,
        128_000, 4_096, 3000, _cap("streaming"),
        None),
]

# ---------------------------------------------------------------------------
# Nscale
# ---------------------------------------------------------------------------
NSCALE_MODELS = [
    _mk("meta-llama/Llama-3.1-70B-Instruct", "nscale", "Llama 3.1 70B (Nscale)", ModelFamily.LLAMA,
        128_000, 4_096, 1200, _cap("streaming", "tool_use"),
        ModelPricing(0.60, 0.80)),
]

# ---------------------------------------------------------------------------
# Lambda Labs
# ---------------------------------------------------------------------------
LAMBDA_MODELS = [
    _mk("llama3.3-70b-instruct-fp8", "lambda_api", "Llama 3.3 70B (Lambda)", ModelFamily.LLAMA,
        128_000, 8_192, 700, _cap("streaming", "tool_use", "function_calling"),
        ModelPricing(0.60, 0.60)),
]

# ---------------------------------------------------------------------------
# OpenCode (GitHub Copilot / code-specialized)
# ---------------------------------------------------------------------------
OPENCODE_MODELS = [
    _mk("opencode/default", "opencode", "OpenCode Default", ModelFamily.OPEN_SOURCE,
        64_000, 4_096, 2000, _cap("streaming"),
        None),
]

# ---------------------------------------------------------------------------
# GitHub (API access to Copilot models)
# ---------------------------------------------------------------------------
GITHUB_MODELS = [
    _mk("github/copilot-4o", "github", "GitHub Copilot (GPT-4o)", ModelFamily.GPT,
        128_000, 16_384, 2000, _cap("streaming", "tool_use", "function_calling"),
        None),
]

# ---------------------------------------------------------------------------
# Ollama (local — stub entry; actual models depend on what's pulled)
# ---------------------------------------------------------------------------
OLLAMA_MODELS = [
    _mk("ollama/llama3.2", "ollama", "Llama 3.2 (Ollama local)", ModelFamily.LLAMA,
        128_000, 4_096, 3000, _cap("streaming", "tool_use"),
        ModelPricing(0.0, 0.0)),
]

# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------
ALL_SEED_MODELS: list[ModelMetadata] = (
    ANTHROPIC_MODELS
    + OPENAI_MODELS
    + GEMINI_MODELS
    + DEEPSEEK_MODELS
    + GROQ_MODELS
    + MISTRAL_MODELS
    + XAI_MODELS
    + NVIDIA_MODELS
    + CEREBRAS_MODELS
    + SAMBANOVA_MODELS
    + TOGETHER_MODELS
    + OPENROUTER_MODELS
    + CLOUDFLARE_MODELS
    + PERPLEXITY_MODELS
    + COHERE_MODELS
    + AI21_MODELS
    + FIREWORKS_MODELS
    + DEEPINFRA_MODELS
    + HUGGINGFACE_MODELS
    + NSCALE_MODELS
    + LAMBDA_MODELS
    + OPENCODE_MODELS
    + GITHUB_MODELS
    + OLLAMA_MODELS
)

__all__ = ["ALL_SEED_MODELS"]
