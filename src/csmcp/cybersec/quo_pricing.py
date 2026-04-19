"""Quota and pricing tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


@tool("check_quota", "Check remaining API quota for one or all providers.", {"provider": {"type": "string", "nullable": True}})
async def check_quota(args: dict[str, Any]) -> JsonDict:
    provider = args.get("provider")
    # Stub: simulate quota check
    quotas = {
        "openai": {"used": 85000, "limit": 100000, "remaining": 15000, "reset_date": "2026-05-01"},
        "anthropic": {"used": 120000, "limit": 200000, "remaining": 80000, "reset_date": "2026-05-01"},
        "google": {"used": 50000, "limit": 100000, "remaining": 50000, "reset_date": "2026-05-01"},
    }
    if provider:
        if provider not in quotas:
            return sdk_error(f"Provider '{provider}' not found")
        return sdk_result({"status": "success", "provider": provider, "quota": quotas[provider]})
    return sdk_result({"status": "success", "quotas": quotas})


@tool("cost_report", "Cost report for session/day/week/month.", {"period": {"type": "string", "enum": ["session", "day", "week", "month"], "default": "session"}})
async def cost_report(args: dict[str, Any]) -> JsonDict:
    period = args.get("period", "session")
    # Stub: simulate cost report
    reports = {
        "session": {
            "period": "session",
            "total_cost_usd": 12.45,
            "total_tokens": 125000,
            "requests": 450,
            "by_provider": {
                "openai": {"cost_usd": 8.50, "tokens": 85000, "requests": 320},
                "anthropic": {"cost_usd": 3.95, "tokens": 40000, "requests": 130},
            },
            "by_model": {
                "gpt-4o": {"cost_usd": 6.20, "tokens": 62000},
                "claude-3-5-sonnet-20241022": {"cost_usd": 3.95, "tokens": 40000},
                "gpt-4o-mini": {"cost_usd": 2.30, "tokens": 23000},
            },
        },
        "day": {"period": "day", "total_cost_usd": 45.20, "total_tokens": 452000, "requests": 1800},
        "week": {"period": "week", "total_cost_usd": 312.80, "total_tokens": 3128000, "requests": 12500},
        "month": {"period": "month", "total_cost_usd": 1250.00, "total_tokens": 12500000, "requests": 50000},
    }
    report = reports.get(period, reports["session"])
    return sdk_result({"status": "success", "report": report})


@tool("list_models_catalog", "All available AI models across providers with capabilities + pricing.", {})
async def list_models_catalog(args: dict[str, Any]) -> JsonDict:
    # Stub: simulate models catalog
    models = [
        {
            "id": "gpt-4o",
            "owned_by": "openai",
            "capabilities": ["chat", "vision", "tools"],
            "context_window": 128000,
            "pricing": {"input": 2.5, "output": 10.0},  # per 1M tokens
            "status": "available",
        },
        {
            "id": "claude-3-5-sonnet-20241022",
            "owned_by": "anthropic",
            "capabilities": ["chat", "vision", "tools"],
            "context_window": 200000,
            "pricing": {"input": 3.0, "output": 15.0},
            "status": "available",
        },
        {
            "id": "gemini-1.5-pro",
            "owned_by": "google",
            "capabilities": ["chat", "vision", "tools"],
            "context_window": 2097152,
            "pricing": {"input": 1.25, "output": 5.0},
            "status": "available",
        },
        {
            "id": "gpt-4o-mini",
            "owned_by": "openai",
            "capabilities": ["chat", "tools"],
            "context_window": 128000,
            "pricing": {"input": 0.15, "output": 0.6},
            "status": "available",
        },
        {
            "id": "claude-3-5-haiku-20241022",
            "owned_by": "anthropic",
            "capabilities": ["chat", "tools"],
            "context_window": 200000,
            "pricing": {"input": 0.25, "output": 1.25},
            "status": "available",
        },
    ]
    return sdk_result({"status": "success", "models": models, "count": len(models)})


ALL_TOOLS = [check_quota, cost_report, list_models_catalog]
