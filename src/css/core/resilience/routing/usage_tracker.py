"""Per-request usage tracking with in-memory ring buffer and best-effort DB."""

from collections import deque
from dataclasses import dataclass

import msgspec


class UsageRecord(msgspec.Struct, frozen=True, kw_only=True):
    provider_id: str
    model_id: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    stream: bool = False
    success: bool = True
    error: str | None = None
    request_id: str | None = None


@dataclass
class _UsageSummary:
    total_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost_usd: float = 0.0
    total_latency_ms: float = 0.0
    successful_requests: int = 0
    failed_requests: int = 0


class UsageTracker:
    """In-memory usage tracker with best-effort DB persistence."""

    def __init__(self, ring_size: int = 10_000) -> None:
        self._buffer: deque[UsageRecord] = deque(maxlen=ring_size)
        self._db_enabled = False

    def record(self, rec: UsageRecord) -> None:
        self._buffer.append(rec)

        if not self._db_enabled:
            return

        try:
            from css.core.db.models.usage import ApiUsageLog

            async def _persist() -> None:
                await ApiUsageLog.create(
                    provider_id=rec.provider_id,
                    model_id=rec.model_id,
                    prompt_tokens=rec.prompt_tokens,
                    completion_tokens=rec.completion_tokens,
                    cost_usd=rec.cost_usd,
                    latency_ms=rec.latency_ms,
                    stream=rec.stream,
                    success=rec.success,
                    error=rec.error,
                    request_id=rec.request_id,
                )

            import asyncio

            try:
                asyncio.create_task(_persist())
            except RuntimeError:
                pass
        except Exception:
            pass

    def record_from_response(
        self,
        provider_id: str,
        model_id: str,
        response: object,
        latency_ms: float,
        request_id: str | None = None,
        stream: bool = False,
        success: bool = True,
        error: str | None = None,
    ) -> UsageRecord:
        prompt_tokens = 0
        completion_tokens = 0
        cost_usd = 0.0

        if isinstance(response, dict):
            usage = response.get("usage") or {}
            prompt_tokens = usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0) or 0
            completion_tokens = usage.get("completion_tokens", 0) or usage.get("output_tokens", 0) or 0

        rec = UsageRecord(
            provider_id=provider_id,
            model_id=model_id,
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(completion_tokens),
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            stream=stream,
            success=success,
            error=error,
            request_id=request_id,
        )
        self.record(rec)
        return rec

    def get_summary(self) -> dict[str, int | float]:
        summary = _UsageSummary()
        for rec in self._buffer:
            summary.total_requests += 1
            summary.total_prompt_tokens += rec.prompt_tokens
            summary.total_completion_tokens += rec.completion_tokens
            summary.total_cost_usd += rec.cost_usd
            summary.total_latency_ms += rec.latency_ms
            if rec.success:
                summary.successful_requests += 1
            else:
                summary.failed_requests += 1

        return {
            "total_requests": summary.total_requests,
            "total_prompt_tokens": summary.total_prompt_tokens,
            "total_completion_tokens": summary.total_completion_tokens,
            "total_cost_usd": round(summary.total_cost_usd, 6),
            "total_latency_ms": summary.total_latency_ms,
            "successful_requests": summary.successful_requests,
            "failed_requests": summary.failed_requests,
        }

    def get_recent(self, limit: int = 10) -> list[UsageRecord]:
        return list(self._buffer)[-limit:]


usage_tracker: UsageTracker = UsageTracker()
