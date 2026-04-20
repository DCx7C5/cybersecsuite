"""
Usage Tracker — log token counts, costs, and latency per request.

Stores usage in-memory with optional PostgreSQL persistence via
the existing Tortoise ORM ApiUsageLog model.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("ai_proxy.usage")


@dataclass
class UsageRecord:
    provider_id: str
    model_id: str
    worktree_sid: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    stream: bool = False
    success: bool = True
    error: str | None = None
    request_id: str | None = None


class UsageTracker:
    """In-memory usage tracker with optional DB persistence."""

    def __init__(self, max_history: int = 10_000) -> None:
        self._records: list[UsageRecord] = []
        self._max_history = max_history
        self._totals: dict[str, dict[str, float]] = {}  # provider -> {tokens, cost, requests}

    def record(self, rec: UsageRecord) -> None:
        self._records.append(rec)
        if len(self._records) > self._max_history:
            self._records = self._records[-self._max_history:]

        key = rec.provider_id
        if key not in self._totals:
            self._totals[key] = {"tokens": 0, "cost": 0.0, "requests": 0, "errors": 0}

        self._totals[key]["tokens"] += rec.total_tokens
        self._totals[key]["cost"] += rec.cost_usd
        self._totals[key]["requests"] += 1
        if not rec.success:
            self._totals[key]["errors"] += 1

    def record_from_response(
        self,
        provider_id: str,
        model_id: str,
        response_body: dict[str, Any] | None,
        latency_ms: float,
        input_cost_per_1m: float = 0.0,
        output_cost_per_1m: float = 0.0,
        worktree_sid: str | None = None,
        stream: bool = False,
        success: bool = True,
        error: str | None = None,
        request_id: str | None = None,
    ) -> UsageRecord:
        """Extract usage from OpenAI-format response and record it."""
        usage = (response_body or {}).get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total = prompt_tokens + completion_tokens

        cost = (
            (prompt_tokens / 1_000_000) * input_cost_per_1m +
            (completion_tokens / 1_000_000) * output_cost_per_1m
        )

        rec = UsageRecord(
            provider_id=provider_id,
            model_id=model_id,
            worktree_sid=worktree_sid,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            cost_usd=cost,
            latency_ms=latency_ms,
            stream=stream,
            success=success,
            error=error,
            request_id=request_id,
        )
        self.record(rec)
        return rec

    def get_summary(self) -> dict[str, Any]:
        """Return usage summary across all providers."""
        total_tokens = sum(t["tokens"] for t in self._totals.values())
        total_cost = sum(t["cost"] for t in self._totals.values())
        total_requests = sum(t["requests"] for t in self._totals.values())
        total_errors = sum(t["errors"] for t in self._totals.values())

        return {
            "total_tokens": int(total_tokens),
            "total_cost_usd": round(total_cost, 6),
            "total_requests": int(total_requests),
            "total_errors": int(total_errors),
            "by_provider": {
                pid: {
                    "tokens": int(stats["tokens"]),
                    "cost_usd": round(stats["cost"], 6),
                    "requests": int(stats["requests"]),
                    "errors": int(stats["errors"]),
                }
                for pid, stats in self._totals.items()
            },
        }

    def get_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return recent usage records."""
        records = self._records[-limit:]
        return [
            {
                "provider": r.provider_id,
                "model": r.model_id,
                "worktree_sid": r.worktree_sid,
                "tokens": r.total_tokens,
                "cost_usd": round(r.cost_usd, 6),
                "latency_ms": round(r.latency_ms, 1),
                "success": r.success,
                "stream": r.stream,
                "request_id": r.request_id,
            }
            for r in reversed(records)
        ]

    def reset(self) -> None:
        self._records.clear()
        self._totals.clear()


# Global singleton
usage_tracker = UsageTracker()
