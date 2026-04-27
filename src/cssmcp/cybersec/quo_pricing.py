"""Quota and pricing tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from cssmcp._sdk_compat import tool
from cssmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


@tool(
    "check_quota",
    "Check rate limit and budget quota for a provider or all providers.",
    {"provider": {"type": "string", "nullable": True}},
)
async def check_quota(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.providers.registry import get_all_providers
        from ai_proxy.services.rate_limiter import rate_limiter
        from ai_proxy.routing.combo import budget_guard
    except ImportError:
        return sdk_error("ai_proxy not available")

    filter_provider = args.get("provider")
    providers = get_all_providers()
    if filter_provider and filter_provider not in providers:
        return sdk_error(f"Provider '{filter_provider}' not found")

    budgets = budget_guard.get_all()
    targets = [filter_provider] if filter_provider else list(providers.keys())

    quotas = {}
    for pid in targets:
        p = providers[pid]
        rate_status = rate_limiter.get_status(pid)
        provider_budget = budgets.get(pid)
        spent = budget_guard.get_spent(pid) if provider_budget is not None else None
        quotas[pid] = {
            "available": p.is_available,
            "rate_limit": rate_status,
            "budget_usd": provider_budget,
            "spent_usd": round(spent, 6) if spent is not None else None,
            "budget_remaining_usd": round(provider_budget - spent, 6) if (provider_budget is not None and spent is not None) else None,
        }

    if filter_provider:
        return sdk_result({"status": "success", "provider": filter_provider, **quotas[filter_provider]})
    return sdk_result({"status": "success", "quotas": quotas})


@tool(
    "cost_report",
    "Cost and usage report broken down by provider. Optional limit on recent records.",
    {"limit": {"type": "integer", "nullable": True}},
)
async def cost_report(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.services.usage_tracker import usage_tracker
    except ImportError:
        return sdk_error("ai_proxy not available")

    limit = int(args.get("limit") or 20)
    summary = usage_tracker.get_summary()
    recent = usage_tracker.get_recent(limit=limit)

    top_providers = sorted(
        summary["by_provider"].items(),
        key=lambda kv: kv[1]["cost_usd"],
        reverse=True,
    )

    return sdk_result({
        "status": "success",
        "totals": {
            "requests": summary["total_requests"],
            "tokens": summary["total_tokens"],
            "cost_usd": summary["total_cost_usd"],
            "errors": summary["total_errors"],
        },
        "by_provider": dict(top_providers),
        "recent": recent,
    })


@tool(
    "list_models_catalog",
    "List all available models with context window, cost, and availability.",
    {
        "provider": {"type": "string", "nullable": True},
        "free_only": {"type": "boolean", "nullable": True},
    },
)
async def list_models_catalog(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.providers.registry import list_all_models, get_all_providers
    except ImportError:
        return sdk_error("ai_proxy not available")

    filter_provider = args.get("provider")
    free_only = bool(args.get("free_only", False))
    all_providers = get_all_providers()

    models = list_all_models()

    if filter_provider:
        models = [m for m in models if m.get("provider") == filter_provider]
    if free_only:
        free_pids = {pid for pid, p in all_providers.items() if p.is_free}
        models = [m for m in models if m.get("provider") in free_pids]

    return sdk_result({
        "status": "success",
        "count": len(models),
        "models": models,
    })


ALL_TOOLS = [check_quota, cost_report, list_models_catalog]
