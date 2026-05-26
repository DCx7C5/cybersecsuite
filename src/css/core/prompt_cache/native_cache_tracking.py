"""Automatic provider-native cache tracking and metrics collection.

Monitors provider-native caching (Tier 2) without explicit cache control.
Providers like Anthropic, OpenAI, DeepSeek automatically cache recent
inputs. This module detects when native cache is active and records stats.
"""

from datetime import UTC, datetime
from typing import Any

from css.core.logger import getLogger
from .types import ResponseCacheStats

logger = getLogger(__name__)


class NativeCacheTracker:
    """Tracks provider-native cache hits and usage patterns."""

    def __init__(self):
        """Initialize native cache tracker."""
        self.total_calls = 0
        self.native_hits = 0
        self.native_misses = 0
        self.total_cached_tokens = 0
        self.total_uncached_tokens = 0
        self.estimated_savings_usd = 0.0

    def record_native_cache_event(
        self,
        native_hit: bool,
        input_tokens_cached: int = 0,
        input_tokens_uncached: int = 0,
        cache_cost_ratio: float = 0.1,
    ) -> ResponseCacheStats:
        """Record a provider-native cache hit/miss event.

        Args:
            native_hit: Whether provider-native cache was used
            input_tokens_cached: Tokens served from cache
            input_tokens_uncached: Fresh tokens
            cache_cost_ratio: Cost multiplier for cached tokens

        Returns:
            ResponseCacheStats for this event
        """
        self.total_calls += 1
        if native_hit:
            self.native_hits += 1
        else:
            self.native_misses += 1

        self.total_cached_tokens += input_tokens_cached
        self.total_uncached_tokens += input_tokens_uncached

        uncached_cost = input_tokens_uncached * (1.0 / 1_000_000)
        cached_cost = input_tokens_cached * cache_cost_ratio * (1.0 / 1_000_000)
        savings = max(0.0, uncached_cost - cached_cost)
        self.estimated_savings_usd += savings

        return ResponseCacheStats(
            native_cache_hit=native_hit,
            input_tokens_cached=input_tokens_cached,
            input_tokens_uncached=input_tokens_uncached,
            estimated_savings_usd=savings,
            created_at=datetime.now(UTC),
        )

    @property
    def native_hit_rate(self) -> float:
        """Calculated provider-native cache hit rate."""
        if self.total_calls == 0:
            return 0.0
        return self.native_hits / self.total_calls

    def summary(self) -> dict[str, Any]:
        """Get tracking summary statistics."""
        return {
            "total_calls": self.total_calls,
            "native_hits": self.native_hits,
            "native_misses": self.native_misses,
            "native_hit_rate": self.native_hit_rate,
            "total_cached_tokens": self.total_cached_tokens,
            "total_uncached_tokens": self.total_uncached_tokens,
            "estimated_savings_usd": round(self.estimated_savings_usd, 4),
        }

    def reset(self) -> None:
        """Reset all tracking counters."""
        self.total_calls = 0
        self.native_hits = 0
        self.native_misses = 0
        self.total_cached_tokens = 0
        self.total_uncached_tokens = 0
        self.estimated_savings_usd = 0.0


class NativeCacheDetector:
    """Detects provider-native cache indicators from response metadata.

    Different providers expose cache usage differently:
      - Anthropic: `usage.cache_read_input_tokens` in response
      - OpenAI: Cache-related fields in usage (deferred to OpenAI SDK update)
      - DeepSeek: `usage.cache_creation_input_tokens` + similar
    """

    @staticmethod
    def detect_anthropic_cache_hit(response_data: dict[str, Any]) -> dict[str, int]:
        """Detect Anthropic prompt cache hit from response.

        Anthropic exposes:
          - usage.cache_creation_input_tokens: tokens written to new cache
          - usage.cache_read_input_tokens: tokens read from existing cache
          - usage.input_tokens: total input tokens (includes both above)

        Args:
            response_data: Response dict with 'usage' key

        Returns:
            {
                'input_cached': tokens from cache,
                'input_uncached': fresh tokens,
                'cache_created': new cache tokens (for TTL tracking),
            }
        """
        usage = response_data.get("usage", {})
        cache_read = usage.get("cache_read_input_tokens", 0)
        cache_create = usage.get("cache_creation_input_tokens", 0)
        input_total = usage.get("input_tokens", 0)

        input_uncached = input_total - cache_read - cache_create

        return {
            "input_cached": cache_read,
            "input_uncached": input_uncached,
            "cache_created": cache_create,
        }

    @staticmethod
    def detect_openai_cache_hit(response_data: dict[str, Any]) -> dict[str, int]:
        """Detect OpenAI cache hit from response.

        OpenAI exposes cache usage via completion_tokens_details (if enabled).
        Falls back to 0 if cache metrics not available.

        Args:
            response_data: Response dict with 'usage' key

        Returns:
            {
                'input_cached': tokens from cache,
                'input_uncached': fresh tokens,
                'cache_created': 0 (OpenAI doesn't separate creation),
            }
        """
        usage = response_data.get("usage", {})
        details = usage.get("completion_tokens_details", {})
        cache_tokens = details.get("cached_completion_tokens", 0)

        return {
            "input_cached": cache_tokens,
            "input_uncached": usage.get("prompt_tokens", 0) - cache_tokens,
            "cache_created": 0,
        }

    @staticmethod
    def detect_deepseek_cache_hit(response_data: dict[str, Any]) -> dict[str, int]:
        """Detect DeepSeek cache hit from response.

        DeepSeek exposes:
          - usage.cache_creation_input_tokens: written to cache
          - usage.cache_read_input_tokens: read from cache
          - Similar pattern to Anthropic

        Args:
            response_data: Response dict with 'usage' key

        Returns:
            {
                'input_cached': tokens from cache,
                'input_uncached': fresh tokens,
                'cache_created': new cache tokens,
            }
        """
        usage = response_data.get("usage", {})
        cache_read = usage.get("cache_read_input_tokens", 0)
        cache_create = usage.get("cache_creation_input_tokens", 0)
        input_total = usage.get("input_tokens", 0)

        input_uncached = input_total - cache_read - cache_create

        return {
            "input_cached": cache_read,
            "input_uncached": input_uncached,
            "cache_created": cache_create,
        }

    @staticmethod
    def detect_cache_hit(
        response_data: dict[str, Any],
        provider: str,
    ) -> dict[str, int]:
        """Auto-detect cache hit based on provider type.

        Args:
            response_data: Response dict
            provider: Provider name (anthropic, openai, deepseek, etc.)

        Returns:
            Cache hit metrics dict
        """
        if provider.lower() == "anthropic":
            return NativeCacheDetector.detect_anthropic_cache_hit(response_data)
        elif provider.lower() == "openai":
            return NativeCacheDetector.detect_openai_cache_hit(response_data)
        elif provider.lower() == "deepseek":
            return NativeCacheDetector.detect_deepseek_cache_hit(response_data)
        else:
            return {"input_cached": 0, "input_uncached": 0, "cache_created": 0}
