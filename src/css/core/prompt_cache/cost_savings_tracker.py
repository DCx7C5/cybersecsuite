"""Cost savings tracker for LLM caching across multiple tiers and providers.

Aggregates cache metrics into financial impact reports:
  - Total API calls and cache hit rates
  - Estimated cost reductions per provider
  - ROI on infrastructure (Redis, etc.)
  - Recommendations for cache strategy tuning
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from css.core.logger import getLogger

logger = getLogger(__name__)


class CostSavingsTracker:
    """Tracks cumulative cost savings from all caching strategies."""

    def __init__(self):
        """Initialize cost tracker."""
        self.created_at = datetime.now(UTC)
        self.events: list[dict[str, Any]] = []
        self.total_api_calls = 0
        self.total_cached_tokens = 0
        self.total_uncached_tokens = 0
        self.exact_match_hits = 0
        self.native_cache_hits = 0

    def record_call(
        self,
        provider: str,
        input_tokens_uncached: int,
        input_tokens_cached: int,
        output_tokens: int,
        cache_source: str,
        cost_uncached_per_m: float,
        cost_cached_per_m: float | None = None,
    ) -> float:
        """Record LLM call and calculate cost savings.

        Args:
            provider: Provider name (anthropic, openai, etc.)
            input_tokens_uncached: Fresh input tokens
            input_tokens_cached: Cached input tokens
            output_tokens: Output tokens (never cached)
            cache_source: Where cache came from (exact_match, native_automatic, none)
            cost_uncached_per_m: Cost per M tokens for uncached input
            cost_cached_per_m: Cost per M tokens for cached input (if less)

        Returns:
            Estimated USD savings for this call
        """
        if cost_cached_per_m is None:
            if cache_source == "exact_match":
                cost_cached_per_m = 0.0
            elif cache_source == "native_automatic":
                cost_cached_per_m = cost_uncached_per_m * 0.1
            else:
                cost_cached_per_m = cost_uncached_per_m

        cost_uncached = input_tokens_uncached * cost_uncached_per_m / 1_000_000
        cost_cached = input_tokens_cached * cost_cached_per_m / 1_000_000
        cost_output = output_tokens * (cost_uncached_per_m * 2) / 1_000_000

        total_cost_with_cache = cost_uncached + cost_cached + cost_output
        total_cost_without_cache = (input_tokens_uncached + input_tokens_cached + output_tokens) * cost_uncached_per_m / 1_000_000

        savings = max(0.0, total_cost_without_cache - total_cost_with_cache)

        self.total_api_calls += 1
        self.total_uncached_tokens += input_tokens_uncached
        self.total_cached_tokens += input_tokens_cached

        if cache_source == "exact_match":
            self.exact_match_hits += 1
        elif cache_source == "native_automatic":
            self.native_cache_hits += 1

        self.events.append({
            "timestamp": datetime.now(UTC),
            "provider": provider,
            "input_uncached": input_tokens_uncached,
            "input_cached": input_tokens_cached,
            "output_tokens": output_tokens,
            "cache_source": cache_source,
            "cost_uncached_per_m": cost_uncached_per_m,
            "cost_cached_per_m": cost_cached_per_m,
            "savings_usd": savings,
        })

        return savings

    def get_cumulative_savings(self) -> float:
        """Get total estimated USD savings to date."""
        return sum(event.get("savings_usd", 0) for event in self.events)

    def get_by_provider(self) -> dict[str, Any]:
        """Get aggregated stats by provider."""
        by_provider: dict[str, Any] = {}

        for event in self.events:
            provider = event["provider"]
            if provider not in by_provider:
                by_provider[provider] = {
                    "calls": 0,
                    "cached_tokens": 0,
                    "uncached_tokens": 0,
                    "total_savings_usd": 0.0,
                    "cache_hit_rate": 0.0,
                }

            stats = by_provider[provider]
            stats["calls"] += 1
            stats["cached_tokens"] += event["input_cached"]
            stats["uncached_tokens"] += event["input_uncached"]
            stats["total_savings_usd"] += event["savings_usd"]

        for provider in by_provider:
            stats = by_provider[provider]
            total_input = stats["cached_tokens"] + stats["uncached_tokens"]
            if total_input > 0:
                stats["cache_hit_rate"] = stats["cached_tokens"] / total_input

        return by_provider

    def get_by_cache_source(self) -> dict[str, Any]:
        """Get aggregated stats by cache strategy."""
        by_source: dict[str, Any] = {}

        for event in self.events:
            source = event["cache_source"]
            if source not in by_source:
                by_source[source] = {
                    "hits": 0,
                    "cached_tokens": 0,
                    "total_savings_usd": 0.0,
                }

            stats = by_source[source]
            stats["hits"] += 1
            stats["cached_tokens"] += event["input_cached"]
            stats["total_savings_usd"] += event["savings_usd"]

        return by_source

    def get_hourly_trend(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get hourly savings trend over last N hours.

        Args:
            hours: Number of hours to aggregate

        Returns:
            List of hourly buckets with cumulative savings
        """
        now = datetime.now(UTC)
        cutoff = now - timedelta(hours=hours)

        hourly: dict[str, dict[str, Any]] = {}

        for event in self.events:
            ts = event["timestamp"]
            if ts < cutoff:
                continue

            hour_bucket = ts.replace(minute=0, second=0, microsecond=0)
            hour_key = hour_bucket.isoformat()

            if hour_key not in hourly:
                hourly[hour_key] = {"timestamp": hour_bucket, "savings_usd": 0.0, "calls": 0}

            hourly[hour_key]["savings_usd"] += event["savings_usd"]
            hourly[hour_key]["calls"] += 1

        return sorted(hourly.values(), key=lambda x: x["timestamp"])

    def summary(self) -> dict[str, Any]:
        """Get comprehensive summary report."""
        cumulative = self.get_cumulative_savings()
        by_provider = self.get_by_provider()
        by_source = self.get_by_cache_source()

        total_input = self.total_cached_tokens + self.total_uncached_tokens
        overall_cache_hit_rate = (
            self.total_cached_tokens / total_input if total_input > 0 else 0.0
        )

        return {
            "period_start": self.created_at.isoformat(),
            "period_end": datetime.now(UTC).isoformat(),
            "total_api_calls": self.total_api_calls,
            "total_cached_tokens": self.total_cached_tokens,
            "total_uncached_tokens": self.total_uncached_tokens,
            "overall_cache_hit_rate": round(overall_cache_hit_rate, 4),
            "exact_match_hits": self.exact_match_hits,
            "native_cache_hits": self.native_cache_hits,
            "cumulative_savings_usd": round(cumulative, 4),
            "average_savings_per_call": round(cumulative / max(1, self.total_api_calls), 6),
            "by_provider": by_provider,
            "by_cache_source": by_source,
        }

    def reset(self) -> None:
        """Reset all tracking data."""
        self.created_at = datetime.now(UTC)
        self.events = []
        self.total_api_calls = 0
        self.total_cached_tokens = 0
        self.total_uncached_tokens = 0
        self.exact_match_hits = 0
        self.native_cache_hits = 0
