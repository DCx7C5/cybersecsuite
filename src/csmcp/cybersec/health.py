"""Health and metrics tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, sdk_result


@tool("get_health", "Health check: uptime, memory, circuit breakers, rate limits, cache stats.", {})
async def get_health(args: dict[str, Any]) -> JsonDict:
    # Stub: simulate health check
    health = {
        "status": "healthy",
        "uptime_seconds": 86400,  # 1 day
        "version": "1.0.0",
        "memory_usage_mb": 256,
        "cpu_usage_percent": 15.5,
        "circuit_breakers": {"total": 25, "open": 2, "closed": 23},
        "rate_limits": {"active_limits": 10, "hits_last_hour": 450},
        "cache_stats": {"hits": 1250, "misses": 320, "hit_rate": 0.796},
        "active_connections": 12,
        "last_error": None,
        "services": {
            "ai_proxy": "healthy",
            "database": "healthy",
            "cache": "healthy",
            "rate_limiter": "healthy",
        },
    }
    return sdk_result({"status": "success", "health": health})


@tool("get_provider_metrics", "Per-provider: latency percentiles, success rate, quota, circuit breaker state.", {"provider": {"type": "string", "nullable": True}})
async def get_provider_metrics(args: dict[str, Any]) -> JsonDict:
    provider = args.get("provider")
    # Stub: simulate provider metrics
    all_metrics = {
        "openai": {
            "requests_total": 1500,
            "success_rate": 0.965,
            "avg_latency_ms": 1200,
            "p95_latency_ms": 2500,
            "p99_latency_ms": 4000,
            "quota_used_percent": 85.0,
            "circuit_breaker_state": "closed",
            "errors_last_hour": 5,
            "cost_last_24h": 45.20,
        },
        "anthropic": {
            "requests_total": 1200,
            "success_rate": 0.978,
            "avg_latency_ms": 1400,
            "p95_latency_ms": 2800,
            "p99_latency_ms": 4500,
            "quota_used_percent": 60.0,
            "circuit_breaker_state": "closed",
            "errors_last_hour": 2,
            "cost_last_24h": 38.50,
        },
        "google": {
            "requests_total": 800,
            "success_rate": 0.952,
            "avg_latency_ms": 1100,
            "p95_latency_ms": 2200,
            "p99_latency_ms": 3500,
            "quota_used_percent": 50.0,
            "circuit_breaker_state": "closed",
            "errors_last_hour": 8,
            "cost_last_24h": 12.80,
        },
    }
    if provider:
        if provider not in all_metrics:
            return sdk_result({"status": "error", "error": f"Provider '{provider}' not found"})
        return sdk_result({"status": "success", "provider": provider, "metrics": all_metrics[provider]})
    return sdk_result({"status": "success", "providers": all_metrics})


@tool("get_session_snapshot", "Full session snapshot: cost, tokens, top models, errors, budget status.", {})
async def get_session_snapshot(args: dict[str, Any]) -> JsonDict:
    # Stub: simulate session snapshot
    snapshot = {
        "session_id": "sess_20260419_001",
        "start_time": "2026-04-19T08:00:00Z",
        "duration_seconds": 14400,  # 4 hours
        "total_requests": 450,
        "successful_requests": 432,
        "failed_requests": 18,
        "success_rate": 0.96,
        "total_cost_usd": 12.45,
        "total_tokens": 125000,
        "budget_status": {
            "allocated_usd": 50.00,
            "used_usd": 12.45,
            "remaining_usd": 37.55,
            "utilization_percent": 24.9,
        },
        "top_models": [
            {"model": "gpt-4o", "requests": 180, "cost_usd": 8.50},
            {"model": "claude-3-5-sonnet-20241022", "requests": 150, "cost_usd": 3.95},
            {"model": "gpt-4o-mini", "requests": 120, "cost_usd": 2.30},
        ],
        "errors_by_type": {
            "rate_limit": 8,
            "timeout": 5,
            "server_error": 3,
            "auth_error": 2,
        },
        "circuit_breaker_events": 3,
        "cache_performance": {"hit_rate": 0.78, "saved_tokens": 25000},
    }
    return sdk_result({"status": "success", "snapshot": snapshot})


ALL_TOOLS = [get_health, get_provider_metrics, get_session_snapshot]
