"""Multi-tier prompt cache orchestrator.

Manages decision logic for which cache tier to use per request:
  - Tier 1 (Exact Redis): Fast O(1) lookup for exact message matches
  - Tier 2 (Native): Provider-native caching when supported
  - Tier 3 (Resource): Explicit resource caching (deferred Phase 12)
"""

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from css.core.logger import getLogger
from .anthropic_breakpoints import inject_cache_breakpoints, estimate_message_tokens
from .types import CachingCapability, ResponseCacheStats

logger = getLogger(__name__)


class PromptCacheManager:
    """Orchestrator for multi-tier prompt caching strategies."""

    def __init__(
        self,
        adapter: Any,
        use_exact_match: bool = True,
        use_native: bool = True,
        use_native_resource: bool = False,
    ):
        """Initialize cache manager for a specific adapter.

        Args:
            adapter: LLMAdapter instance with cache_capability property
            use_exact_match: Enable Tier 1 (Redis exact-match)
            use_native: Enable Tier 2 (provider-native automatic)
            use_native_resource: Enable Tier 3 (resource caching, usually deferred)
        """
        self.adapter = adapter
        self.use_exact_match = use_exact_match
        self.use_native = use_native
        self.use_native_resource = use_native_resource

    @property
    def cache_capability(self) -> CachingCapability:
        """Get adapter's caching capability level."""
        return self.adapter.cache_capability

    def prepare_messages_for_caching(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Prepare messages for caching based on capability.

        Returns modified messages + metadata for cache stats recording.

        For Anthropic with explicit breakpoints capability:
          - Inject cache_control tokens for advanced layouts
          - Support per-N-message ephemeral breakpoints

        Args:
            messages: Input message list
            model: Model identifier (reserved for per-model tuning)

        Returns:
            (modified_messages, cache_metadata)
        """
        metadata: dict[str, Any] = {}
        modified = messages

        if self.cache_capability == CachingCapability.NATIVE_AUTOMATIC_WITH_EXPLICIT_BREAKPOINTS:
            modified = inject_cache_breakpoints(
                messages,
                ephemeral_breakpoint_every_n_messages=5,
                model=model,
            )
            metadata["anthropic_breakpoints_injected"] = True

        return modified, metadata

    def compute_exact_match_key(
        self,
        messages: list[dict[str, Any]],
        model: str,
        system_prompt: str | None = None,
    ) -> str:
        """Compute Redis key for exact-match cache lookup.

        Hashes (messages, model, system_prompt) for O(1) cache hit detection.

        Args:
            messages: Input message list
            model: Model ID
            system_prompt: Optional system prompt

        Returns:
            Hex-encoded SHA256 hash suitable as Redis key
        """
        payload = {
            "messages": messages,
            "model": model,
            "system_prompt": system_prompt,
        }
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        key_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        return f"prompt_cache:exact:{key_hash}"

    def estimate_cache_savings(
        self,
        messages: list[dict[str, Any]],
        input_tokens_cached: int,
        input_tokens_uncached: int,
        cache_cost_ratio: float = 0.1,
    ) -> float:
        """Estimate USD savings from caching.

        Simple heuristic: assumes $1 per M input tokens uncached,
        cached tokens cost cache_cost_ratio of that.

        Args:
            messages: Message list (unused for now)
            input_tokens_cached: Tokens served from cache
            input_tokens_uncached: Fresh tokens processed
            cache_cost_ratio: Cost multiplier for cached tokens (e.g., 0.1 for Anthropic)

        Returns:
            Estimated USD savings
        """
        uncached_cost = input_tokens_uncached * (1.0 / 1_000_000)
        cached_cost = input_tokens_cached * cache_cost_ratio * (1.0 / 1_000_000)
        savings = uncached_cost - cached_cost
        return max(0.0, savings)

    def record_cache_stats(
        self,
        exact_hit: bool = False,
        native_hit: bool = False,
        native_created: bool = False,
        input_cached: int = 0,
        input_uncached: int = 0,
        output_tokens: int = 0,
        cache_key: str | None = None,
    ) -> ResponseCacheStats:
        """Record cache statistics for a single response.

        Args:
            exact_hit: Response came from exact-match Redis
            native_hit: Response used provider-native cache
            native_created: Response created new provider-native cache entry
            input_cached: Tokens from cache (not re-encoded)
            input_uncached: Fresh input tokens
            output_tokens: Output tokens (never cached)
            cache_key: Redis key if exact_hit=True

        Returns:
            ResponseCacheStats struct
        """
        cache_cost_ratio = 0.1 if self.cache_capability in (
            CachingCapability.NATIVE_AUTOMATIC,
            CachingCapability.NATIVE_AUTOMATIC_WITH_EXPLICIT_BREAKPOINTS,
        ) else 0.0

        savings = self.estimate_cache_savings(
            [],
            input_tokens_cached=input_cached,
            input_tokens_uncached=input_uncached,
            cache_cost_ratio=cache_cost_ratio,
        )

        return ResponseCacheStats(
            exact_match_hit=exact_hit,
            native_cache_hit=native_hit,
            native_cache_created=native_created,
            input_tokens_cached=input_cached,
            input_tokens_uncached=input_uncached,
            output_tokens=output_tokens,
            estimated_savings_usd=savings,
            cache_key_hash=cache_key,
            created_at=datetime.now(UTC),
        )

    def select_tier(
        self,
        messages: list[dict[str, Any]],
        model: str,
        system_prompt: str | None = None,
    ) -> tuple[int, dict[str, Any]]:
        """Select best cache tier for this request.

        Decision tree:
          1. Capability NONE → Tier 3 (no caching, return stats only)
          2. Exact-only → Tier 1 (Redis only)
          3. Native auto → Tier 2 (provider-native, no explicit control)
          4. Native + breakpoints → Tier 2 (provider-native + inject controls)
          5. Resource-based → Tier 3 (explicit creation, deferred)

        Args:
            messages: Input messages
            model: Model ID
            system_prompt: Optional system prompt

        Returns:
            (tier: 1|2|3, decision_metadata: dict)
        """
        metadata = {
            "capability": self.cache_capability.value,
            "message_count": len(messages),
            "estimated_tokens": sum(estimate_message_tokens(m) for m in messages),
        }

        if self.cache_capability == CachingCapability.NONE:
            return 3, {**metadata, "tier": 3, "reason": "no_caching_support"}

        if self.cache_capability == CachingCapability.EXACT_ONLY:
            if self.use_exact_match:
                return 1, {**metadata, "tier": 1, "reason": "exact_match_only"}
            return 3, {**metadata, "tier": 3, "reason": "exact_match_disabled"}

        if self.cache_capability in (
            CachingCapability.NATIVE_AUTOMATIC,
            CachingCapability.NATIVE_AUTOMATIC_WITH_EXPLICIT_BREAKPOINTS,
        ):
            if self.use_native:
                return 2, {**metadata, "tier": 2, "reason": "native_auto"}
            return 3, {**metadata, "tier": 3, "reason": "native_disabled"}

        if self.cache_capability == CachingCapability.NATIVE_RESOURCE:
            if self.use_native_resource:
                return 3, {**metadata, "tier": 3, "reason": "resource_explicit", "deferred": True}
            return 3, {**metadata, "tier": 3, "reason": "resource_disabled"}

        return 3, {**metadata, "tier": 3, "reason": "unknown_capability"}
