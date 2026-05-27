"""Tier filtering for provider-routing candidate chains."""

from collections.abc import Sequence
from typing import Mapping

from .strategy import PROVIDER_TIER_LIST, ProviderTier
from .triage import RequestComplexity

_CEILING_RANK: dict[str, int] = {
    "SIMPLE": 1,
    "MODERATE": 2,
    "COMPLEX": 3,
    "CRITICAL": 4,
}

_REQUEST_RANK: dict[RequestComplexity, int] = {
    RequestComplexity.TRIVIAL: 0,
    RequestComplexity.SIMPLE: 1,
    RequestComplexity.MODERATE: 2,
    RequestComplexity.COMPLEX: 3,
    RequestComplexity.CRITICAL: 4,
}


def _max_available_vram(available_hardware: Sequence[Mapping[str, object]]) -> float:
    max_vram = 0.0
    for item in available_hardware:
        raw_vram = item.get("vram_gb")
        if isinstance(raw_vram, int | float):
            max_vram = max(max_vram, float(raw_vram))
    return max_vram


def _supports_runtime(tier: ProviderTier, available_hardware: Sequence[Mapping[str, object]]) -> bool:
    if "Ollama" not in tier.runtime:
        return True
    return _max_available_vram(available_hardware) >= tier.min_vram_gb


def _fits_complexity(tier: ProviderTier, complexity: RequestComplexity) -> bool:
    tier_ceiling = _CEILING_RANK.get(tier.complexity_ceiling.upper(), 0)
    return tier_ceiling >= _REQUEST_RANK[complexity]


def _fits_budget(tier: ProviderTier, budget_remaining_usd: float) -> bool:
    if budget_remaining_usd < 0:
        return False
    estimated_cost = tier.input_cost_per_mtok + tier.output_cost_per_mtok
    if estimated_cost <= 0:
        return True
    return estimated_cost <= budget_remaining_usd


class TierSelector:
    """Pure tier candidate selector based on constraints."""

    @staticmethod
    def filter(
        complexity: RequestComplexity,
        budget_remaining_usd: float,
        available_hardware: Sequence[Mapping[str, object]],
        security_level: int,
    ) -> list[ProviderTier]:
        """Filter provider tiers and always append S_PLUS fallback."""
        terminal = next((tier for tier in PROVIDER_TIER_LIST if tier.name == "S_PLUS"), None)
        if terminal is None:
            return []

        filtered: list[ProviderTier] = []
        for tier in PROVIDER_TIER_LIST:
            if tier.name == "S_PLUS":
                continue
            if security_level >= 9 and tier.rank < 9:
                continue
            if not _fits_complexity(tier, complexity):
                continue
            if not _supports_runtime(tier, available_hardware):
                continue
            if not _fits_budget(tier, budget_remaining_usd):
                continue
            filtered.append(tier)

        filtered.append(terminal)
        return filtered
