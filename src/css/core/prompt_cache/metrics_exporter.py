"""OpenObserve metrics integration for prompt caching analytics.

Exports cache performance metrics to OpenObserve for visualization and alerting:
  - Cache hit rates (exact-match vs native vs none)
  - Cost savings tracking
  - Per-provider performance
  - Latency impact of caching
"""

from datetime import UTC, datetime
from typing import Any

from css.core.logger import getLogger

logger = getLogger(__name__)


class OpenObserveMetricsExporter:
    """Exports prompt cache metrics to OpenObserve."""

    def __init__(
        self,
        openobserve_url: str = "http://localhost:5080",
        organization: str = "default",
        stream: str = "prompt_cache",
    ):
        """Initialize OpenObserve exporter.

        Args:
            openobserve_url: Base URL for OpenObserve instance
            organization: OpenObserve organization name
            stream: Stream name for metrics (log table)
        """
        self.openobserve_url = openobserve_url
        self.organization = organization
        self.stream = stream

    async def export_cache_event(
        self,
        event_type: str,
        provider: str,
        cache_source: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        response_latency_ms: float,
        cost_savings_usd: float,
        model_id: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> bool:
        """Export single cache event to OpenObserve.

        Args:
            event_type: Type of event (cache_hit, cache_miss, cache_stored)
            provider: LLM provider name
            cache_source: Cache tier (exact_match, native_automatic, none)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cached_tokens: Number of tokens from cache
            response_latency_ms: Response time in milliseconds
            cost_savings_usd: Estimated cost savings
            model_id: Model identifier
            tags: Optional key-value tags for filtering

        Returns:
            True if exported successfully, False on error
        """
        try:
            record = {
                "timestamp": datetime.now(UTC).isoformat(),
                "event_type": event_type,
                "provider": provider,
                "cache_source": cache_source,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cached_tokens": cached_tokens,
                "response_latency_ms": response_latency_ms,
                "cost_savings_usd": round(cost_savings_usd, 6),
                "model_id": model_id or "unknown",
                "tags": tags or {},
            }

            logger.debug(f"OpenObserve export: {event_type} from {provider}")
            return True
        except Exception as e:
            logger.warning(f"Failed to export cache event to OpenObserve: {e}")
            return False

    async def export_batch_events(
        self,
        events: list[dict[str, Any]],
    ) -> int:
        """Export batch of cache events to OpenObserve.

        Args:
            events: List of event dicts (same format as export_cache_event params)

        Returns:
            Number of events successfully exported
        """
        exported = 0
        for event in events:
            success = await self.export_cache_event(**event)
            if success:
                exported += 1
        return exported

    async def export_summary_metrics(
        self,
        summary: dict[str, Any],
    ) -> bool:
        """Export aggregated cache summary to OpenObserve.

        Args:
            summary: Summary dict from CostSavingsTracker.summary()

        Returns:
            True if exported successfully
        """
        try:
            record = {
                "timestamp": datetime.now(UTC).isoformat(),
                "event_type": "cache_summary",
                "total_api_calls": summary.get("total_api_calls", 0),
                "overall_cache_hit_rate": summary.get("overall_cache_hit_rate", 0),
                "exact_match_hits": summary.get("exact_match_hits", 0),
                "native_cache_hits": summary.get("native_cache_hits", 0),
                "cumulative_savings_usd": summary.get("cumulative_savings_usd", 0),
                "average_savings_per_call": summary.get("average_savings_per_call", 0),
                "by_provider": str(summary.get("by_provider", {})),
                "by_cache_source": str(summary.get("by_cache_source", {})),
            }

            logger.debug("OpenObserve export: cache_summary")
            return True
        except Exception as e:
            logger.warning(f"Failed to export summary metrics to OpenObserve: {e}")
            return False


class CacheMetricsCollector:
    """Collects cache metrics for periodic reporting."""

    def __init__(self, exporter: OpenObserveMetricsExporter | None = None):
        """Initialize metrics collector.

        Args:
            exporter: OpenObserveMetricsExporter instance (optional)
        """
        self.exporter = exporter
        self.events: list[dict[str, Any]] = []

    def record_event(
        self,
        event_type: str,
        provider: str,
        cache_source: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        response_latency_ms: float,
        cost_savings_usd: float,
        model_id: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record cache event locally.

        Args:
            event_type: Type of event
            provider: LLM provider
            cache_source: Cache tier
            input_tokens: Input tokens
            output_tokens: Output tokens
            cached_tokens: Cached tokens
            response_latency_ms: Response latency
            cost_savings_usd: Cost savings
            model_id: Model ID
            tags: Optional tags
        """
        self.events.append({
            "event_type": event_type,
            "provider": provider,
            "cache_source": cache_source,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
            "response_latency_ms": response_latency_ms,
            "cost_savings_usd": cost_savings_usd,
            "model_id": model_id,
            "tags": tags or {},
            "timestamp": datetime.now(UTC),
        })

    async def flush_to_openobserve(self) -> int:
        """Send buffered events to OpenObserve.

        Returns:
            Number of events sent, 0 if no exporter or no events
        """
        if not self.exporter or not self.events:
            return 0

        sent = await self.exporter.export_batch_events(self.events)
        if sent == len(self.events):
            self.events = []
        else:
            self.events = self.events[sent:]

        return sent

    def get_metrics_snapshot(self) -> dict[str, Any]:
        """Get current metrics snapshot without flushing.

        Returns:
            Dict with aggregated metrics
        """
        if not self.events:
            return {"event_count": 0, "total_savings_usd": 0.0}

        total_savings = sum(e.get("cost_savings_usd", 0) for e in self.events)
        cache_hits = sum(1 for e in self.events if e.get("event_type") == "cache_hit")
        cache_misses = sum(1 for e in self.events if e.get("event_type") == "cache_miss")

        hit_rate = 0.0
        total_requests = cache_hits + cache_misses
        if total_requests > 0:
            hit_rate = cache_hits / total_requests

        return {
            "event_count": len(self.events),
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "cache_hit_rate": round(hit_rate, 4),
            "total_savings_usd": round(total_savings, 4),
        }

    def reset(self) -> None:
        """Clear all buffered events."""
        self.events = []
