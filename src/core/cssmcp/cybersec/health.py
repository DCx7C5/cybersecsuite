"""Health and metrics tools — SDK in-process MCP server module."""
from __future__ import annotations

import os
import time
from typing import Any

from core.cssmcp.sdk_compat import tool
from core.cssmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error

_START_TIME = time.time()


@tool("get_health", "Health check: uptime, circuit breakers, provider status, rate limits, cache.", {})
async def get_health(args: dict[str, Any]) -> JsonDict:
    try:
        from src.registries.providers import get_all_providers
        from ai_proxy.routing.combo import get_circuit_breaker_status
        from ai_proxy.services.rate_limiter import rate_limiter
        from ai_proxy.services.usage_tracker import usage_tracker
    except ImportError:
        return sdk_error("ai_proxy not available")

    providers = get_all_providers()
    cb_status = get_circuit_breaker_status()
    open_cbs = [cb for cb in cb_status if cb["state"] == "open"]
    summary = usage_tracker.get_summary()

    services: dict[str, str] = {"ai_proxy": "healthy", "rate_limiter": "healthy"}
    try:
        from db.main import is_initialized
        services["database"] = "healthy" if is_initialized() else "degraded"
    except Exception:
        services["database"] = "unknown"

    return sdk_result({
        "status": "healthy" if not open_cbs else "degraded",
        "uptime_seconds": round(time.time() - _START_TIME),
        "version": os.environ.get("APP_VERSION", "0.1.0"),
        "providers_total": len(providers),
        "providers_available": sum(1 for p in providers.values() if p.is_available),
        "circuit_breakers": {
            "total": len(cb_status),
            "open": len(open_cbs),
            "closed": len(cb_status) - len(open_cbs),
            "open_targets": [cb["target"] for cb in open_cbs],
        },
        "usage": {
            "total_requests": summary["total_requests"],
            "total_errors": summary["total_errors"],
            "total_cost_usd": summary["total_cost_usd"],
        },
        "rate_limits": {
            p_id: rate_limiter.get_status(p_id) for p_id in providers
        },
        "services": services,
    })


@tool(
    "get_provider_metrics",
    "Per-provider latency (p50/p95/p99), success rate, usage, and circuit breaker state.",
    {"provider": {"type": "string", "nullable": True}},
)
async def get_provider_metrics(args: dict[str, Any]) -> JsonDict:
    try:
        from src.registries.providers import get_all_providers
        from ai_proxy.routing.combo import get_circuit_breaker_status, get_usage_counts
        from ai_proxy.services.usage_tracker import usage_tracker
        from ai_proxy.services.rate_limiter import rate_limiter
    except ImportError:
        return sdk_error("ai_proxy not available")

    filter_provider = args.get("provider")
    providers = get_all_providers()
    if filter_provider and filter_provider not in providers:
        return sdk_error(f"Provider '{filter_provider}' not found")

    cb_status = get_circuit_breaker_status()
    cb_open_targets = {cb["target"] for cb in cb_status if cb["state"] == "open"}
    usage_counts = get_usage_counts()
    summary = usage_tracker.get_summary()
    by_provider = summary["by_provider"]

    metrics: dict[str, Any] = {}
    for p_id, p in providers.items():
        if filter_provider and p_id != filter_provider:
            continue
        p_usage = by_provider.get(p_id, {"tokens": 0, "cost_usd": 0.0, "requests": 0, "errors": 0})
        req_count = p_usage["requests"]
        err_count = p_usage["errors"]
        metrics[p_id] = {
            "available": p.is_available,
            "is_free": p.is_free,
            "requests_total": req_count,
            "errors_total": err_count,
            "success_rate": round((req_count - err_count) / req_count, 4) if req_count else None,
            "tokens_total": p_usage["tokens"],
            "cost_total_usd": p_usage["cost_usd"],
            "usage_count": usage_counts.get(p_id, 0),
            "circuit_breaker_open_targets": [t for t in cb_open_targets if t.startswith(f"{p_id}:")],
            "rate_limit_status": rate_limiter.get_status(p_id),
        }

    if filter_provider:
        return sdk_result({"status": "success", "provider": filter_provider, "metrics": metrics[filter_provider]})
    return sdk_result({"status": "success", "providers": metrics})


@tool("get_session_snapshot", "Full session snapshot: cost, tokens, recent requests, budget, circuit breakers.", {})
async def get_session_snapshot(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.services.usage_tracker import usage_tracker
        from ai_proxy.routing.combo import get_circuit_breaker_status, budget_guard
    except ImportError:
        return sdk_error("ai_proxy not available")

    summary = usage_tracker.get_summary()
    recent = usage_tracker.get_recent(limit=10)
    cb_status = get_circuit_breaker_status()
    open_cbs = [cb for cb in cb_status if cb["state"] == "open"]

    return sdk_result({
        "status": "success",
        "uptime_seconds": round(time.time() - _START_TIME),
        "usage": summary,
        "recent_requests": recent,
        "circuit_breakers": {
            "open": len(open_cbs),
            "total": len(cb_status),
            "open_targets": [cb["target"] for cb in open_cbs],
        },
        "budgets": budget_guard.get_all(),
    })


ALL_TOOLS = [get_health, get_provider_metrics, get_session_snapshot]
