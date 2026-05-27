"""QwenTriageRouter — 10-tier request classification + provider selection."""

from hashlib import sha256
from time import time
from typing import Any

import msgspec

from .strategy import PROVIDER_TIER_LIST, ProviderTier
from .tier_selector import TierSelector
from .token_counter import TokenCounter
from .triage import TriageMetrics, analyze_complexity


class TriageResponse(msgspec.Struct, frozen=True, kw_only=True):
    tier: str
    primary_provider: str | None
    fallback_providers: list[str]
    estimated_cost_cents: float
    reasoning: str
    metrics: TriageMetrics | None = None


class QwenTriageRouter:
    """10-tier request classification with TTL-cached triage decisions."""

    def __init__(
        self,
        token_counter: TokenCounter | None = None,
        cache_ttl: float = 300.0,
    ) -> None:
        self._token_counter = token_counter or TokenCounter()
        self._cache: dict[str, tuple[float, TriageResponse]] = {}
        self._cache_ttl = cache_ttl

    def _hash_request(self, text: str) -> str:
        return sha256(text.encode()).hexdigest()

    def _from_cache(self, query_hash: str) -> TriageResponse | None:
        entry = self._cache.get(query_hash)
        if entry is None:
            return None
        expiry, result = entry
        if time() >= expiry:
            del self._cache[query_hash]
            return None
        return result

    def triage(self, request: object, **kw: Any) -> TriageResponse:
        metrics = self.analyze_complexity(request)
        text_blob = _extract_text(request)
        query_hash = self._hash_request(text_blob)

        cached = self._from_cache(query_hash)
        if cached is not None:
            return cached

        tier = self.determine_minimum_tier(metrics)
        available_hardware = kw.get("available_hardware", [])
        budget_remaining = float(kw.get("budget_remaining_usd", 1.0))
        security_level = metrics.security_level

        candidates = TierSelector.filter(
            complexity=metrics.complexity,
            budget_remaining_usd=budget_remaining,
            available_hardware=available_hardware,
            security_level=security_level,
        )

        primary = self.select_primary_provider(metrics, candidates)
        fallback_chain = self.build_fallback_chain(candidates, primary)
        estimated_cost = self._estimate_cost(metrics, candidates)

        reasoning_parts = [
            f"complexity={metrics.complexity.value}",
            f"tokens={metrics.estimated_tokens}",
            f"tier={tier or 'none'}",
            f"primary={primary or 'none'}",
            f"fallbacks={len(fallback_chain)}",
        ]
        reasoning = ", ".join(reasoning_parts)

        result = TriageResponse(
            tier=tier or "UNKNOWN",
            primary_provider=primary,
            fallback_providers=fallback_chain,
            estimated_cost_cents=estimated_cost,
            reasoning=reasoning,
            metrics=metrics,
        )

        self._cache[query_hash] = (time() + self._cache_ttl, result)
        return result

    def analyze_complexity(self, request: object) -> TriageMetrics:
        return analyze_complexity(request, self._token_counter)

    def determine_minimum_tier(self, metrics: TriageMetrics) -> str | None:
        complexity = metrics.complexity
        for tier in PROVIDER_TIER_LIST:
            if tier.complexity_ceiling.upper() == complexity.value:
                return tier.name
        return PROVIDER_TIER_LIST[0].name if PROVIDER_TIER_LIST else None

    def select_primary_provider(
        self,
        metrics: TriageMetrics,
        candidates: list[ProviderTier],
    ) -> str | None:
        if not candidates:
            return None
        preferred = candidates[0]
        return preferred.representative_models[0] if preferred.representative_models else preferred.name

    def build_fallback_chain(
        self,
        candidates: list[ProviderTier],
        primary: str | None,
    ) -> list[str]:
        chain: list[str] = []
        for tier in candidates:
            for model in tier.representative_models:
                if model != primary:
                    chain.append(tier.name)
                    break
        return chain

    def _estimate_cost(self, metrics: TriageMetrics, candidates: list[ProviderTier]) -> float:
        if not candidates:
            return 0.0
        tier = candidates[0]
        per_mtok = tier.input_cost_per_mtok + tier.output_cost_per_mtok
        if per_mtok <= 0:
            return 0.0
        tokens_k = metrics.estimated_tokens / 1000.0
        return round(tokens_k * per_mtok * 100, 2)


qwen_triage_router: QwenTriageRouter = QwenTriageRouter()


def _extract_text(request: object) -> str:
    if isinstance(request, str):
        return request
    if isinstance(request, dict):
        messages = request.get("messages", request.get("prompt", ""))
        if isinstance(messages, list):
            parts = []
            for msg in messages:
                content = msg.get("content", "") if isinstance(msg, dict) else ""
                parts.append(str(content))
            return " ".join(parts)
        return str(messages)
    return str(request)
