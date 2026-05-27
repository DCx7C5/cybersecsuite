"""Routing strategy and provider-tier value definitions."""

from enum import Enum

import msgspec


class Strategy(str, Enum):
    """Routing strategies supported by combo-based target selection."""

    PRIORITY = "priority"
    ROUND_ROBIN = "round_robin"
    COST_OPTIMIZED = "cost_optimized"
    WEIGHTED = "weighted"
    RANDOM = "random"
    LEAST_USED = "least_used"
    FILL_FIRST = "fill_first"
    P2C = "p2c"
    STRICT_RANDOM = "strict_random"
    LKGP = "lkgp"
    CONTEXT_OPTIMIZED = "context_optimized"
    CONTEXT_RELAY = "context_relay"
    AUTO = "auto"


class ProviderTier(msgspec.Struct, frozen=True, kw_only=True):
    """Ordered provider/model tier metadata used by routing selectors."""

    name: str
    rank: int
    representative_models: list[str]
    complexity_ceiling: str
    runtime: str
    min_vram_gb: float
    input_cost_per_mtok: float
    output_cost_per_mtok: float
    is_terminal: bool = False


PROVIDER_TIER_LIST: list[ProviderTier] = [
    ProviderTier(
        name="LOCAL_MINIMAL",
        rank=0,
        representative_models=["qwen3:0.6b", "llama3.2:1b"],
        complexity_ceiling="SIMPLE",
        runtime="Ollama, CPU only",
        min_vram_gb=0.0,
        input_cost_per_mtok=0.0,
        output_cost_per_mtok=0.0,
    ),
    ProviderTier(
        name="LOCAL_LIGHT",
        rank=1,
        representative_models=["qwen3:1.7b", "llama3.2:3b", "phi3:mini"],
        complexity_ceiling="MODERATE",
        runtime="Ollama, 4 GB VRAM",
        min_vram_gb=4.0,
        input_cost_per_mtok=0.0,
        output_cost_per_mtok=0.0,
    ),
    ProviderTier(
        name="LOCAL_STANDARD",
        rank=2,
        representative_models=["qwen3:4b", "mistral:7b", "llama3.1:8b"],
        complexity_ceiling="MODERATE",
        runtime="Ollama, 8 GB VRAM",
        min_vram_gb=8.0,
        input_cost_per_mtok=0.0,
        output_cost_per_mtok=0.0,
    ),
    ProviderTier(
        name="LOCAL_CAPABLE",
        rank=3,
        representative_models=["qwen3:8b", "llama3.1:8b-q8", "deepseek-r1:8b"],
        complexity_ceiling="COMPLEX",
        runtime="Ollama, 16 GB VRAM",
        min_vram_gb=16.0,
        input_cost_per_mtok=0.0,
        output_cost_per_mtok=0.0,
    ),
    ProviderTier(
        name="FREE_CLOUD",
        rank=4,
        representative_models=["gemini-flash-lite", "groq-free", "together-free"],
        complexity_ceiling="MODERATE",
        runtime="HTTP, free",
        min_vram_gb=0.0,
        input_cost_per_mtok=0.0,
        output_cost_per_mtok=0.0,
    ),
    ProviderTier(
        name="BUDGET_CLOUD",
        rank=5,
        representative_models=["gemini-flash", "deepseek-chat", "grok-mini", "mistral-small"],
        complexity_ceiling="COMPLEX",
        runtime="HTTP, low cost",
        min_vram_gb=0.0,
        input_cost_per_mtok=0.2,
        output_cost_per_mtok=0.6,
    ),
    ProviderTier(
        name="STANDARD_CLOUD",
        rank=6,
        representative_models=["gpt-4o-mini", "claude-haiku", "gemini-pro", "mistral-large"],
        complexity_ceiling="COMPLEX",
        runtime="HTTP or native",
        min_vram_gb=0.0,
        input_cost_per_mtok=1.0,
        output_cost_per_mtok=3.0,
    ),
    ProviderTier(
        name="ADVANCED_CLOUD",
        rank=7,
        representative_models=["gpt-4o", "claude-sonnet", "gemini-pro", "grok"],
        complexity_ceiling="CRITICAL",
        runtime="HTTP or native",
        min_vram_gb=0.0,
        input_cost_per_mtok=3.0,
        output_cost_per_mtok=10.0,
    ),
    ProviderTier(
        name="PREMIUM_CLOUD",
        rank=8,
        representative_models=["gpt-4.5", "claude-sonnet", "gemini-pro", "o3-mini"],
        complexity_ceiling="CRITICAL",
        runtime="Native",
        min_vram_gb=0.0,
        input_cost_per_mtok=8.0,
        output_cost_per_mtok=24.0,
    ),
    ProviderTier(
        name="ELITE_CLOUD",
        rank=9,
        representative_models=["claude-opus", "gpt-5", "o3", "gemini-ultra"],
        complexity_ceiling="CRITICAL",
        runtime="Native",
        min_vram_gb=0.0,
        input_cost_per_mtok=15.0,
        output_cost_per_mtok=45.0,
    ),
    ProviderTier(
        name="S_PLUS",
        rank=10,
        representative_models=["frontier-deep-thinking"],
        complexity_ceiling="CRITICAL",
        runtime="Native, unstable API guard",
        min_vram_gb=0.0,
        input_cost_per_mtok=25.0,
        output_cost_per_mtok=75.0,
        is_terminal=True,
    ),
]
