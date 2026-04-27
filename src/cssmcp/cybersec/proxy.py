"""AI proxy routing tools — SDK in-process MCP server module.

Wraps ai_proxy with 10 MCP tools.
"""
from __future__ import annotations

from typing import Any

from cssmcp._sdk_compat import tool
from cssmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


@tool(
    "proxy_chat",
    "Route a chat completion through the AI proxy with multi-provider fallback.",
    {
        "prompt": "string",
        "model": {"type": "string", "default": "gpt-4o-mini"},
        "provider": {"type": "string", "nullable": True},
        "system": {"type": "string", "nullable": True},
        "prefer_free": {"type": "boolean", "default": False},
        "max_cost_per_1k": {"type": "number", "nullable": True},
        "temperature": {"type": "number", "nullable": True},
        "max_tokens": {"type": "integer", "nullable": True},
    },
)
async def proxy_chat(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.routing.combo import smart_route, route_request, ComboConfig, ComboTarget, Strategy
    except ImportError:
        return sdk_error("ai_proxy not available")

    prompt = args["prompt"]
    model = args.get("model", "gpt-4o-mini")
    provider = args.get("provider")
    system = args.get("system")
    prefer_free = args.get("prefer_free", False)
    max_cost_per_1k = args.get("max_cost_per_1k")
    temperature = args.get("temperature")
    max_tokens = args.get("max_tokens")

    body: JsonDict = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["messages"].insert(0, {"role": "system", "content": system})
    if temperature is not None:
        body["temperature"] = temperature
    if max_tokens is not None:
        body["max_tokens"] = max_tokens

    if provider:
        combo = ComboConfig(
            id=f"mcp-{provider}", name=f"MCP → {provider}", strategy=Strategy.PRIORITY,
            targets=[ComboTarget(provider_id=provider, model_id=model)],
        )
        result = await route_request(body, combo)
    else:
        result = await smart_route(body, prefer_free=prefer_free, max_cost_per_1k=max_cost_per_1k)

    if not result.ok:
        return sdk_result({"status": "error", "error": result.error, "status_code": result.status_code})

    choices = (result.body or {}).get("choices", [])
    content = choices[0].get("message", {}).get("content", "") if choices else ""
    return sdk_result({
        "status": "success", "content": content, "provider": result.provider_id,
        "model": result.model_id, "latency_ms": round(result.latency_ms, 1),
        "usage": (result.body or {}).get("usage", {}),
    })


@tool("proxy_providers", "List all configured AI providers with status and rate limits.", {})
async def proxy_providers(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.providers.registry import get_all_providers
        from ai_proxy.services.rate_limiter import rate_limiter
    except ImportError:
        return sdk_error("ai_proxy not available")

    providers = []
    for p in get_all_providers().values():
        providers.append({
            "id": p.id, "name": p.name, "format": p.api_format.value,
            "is_free": p.is_free, "has_key": p.get_api_key() is not None,
            "models": [m.id for m in p.models], "rate_limit": rate_limiter.get_status(p.id),
        })
    return sdk_result({"status": "success", "providers": providers, "count": len(providers)})


@tool("proxy_models", "List all available models across providers, optionally filtered by provider.", {"provider": {"type": "string", "nullable": True}})
async def proxy_models(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.providers.registry import list_all_models
    except ImportError:
        return sdk_error("ai_proxy not available")

    models = list_all_models()
    if args.get("provider"):
        models = [m for m in models if m["owned_by"] == args["provider"]]
    return sdk_result({"status": "success", "models": models, "count": len(models)})


@tool("proxy_usage", "Return AI proxy usage summary: tokens, costs, requests by provider.", {})
async def proxy_usage(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.services.usage_tracker import usage_tracker
    except ImportError:
        return sdk_error("ai_proxy not available")

    return sdk_result({
        "status": "success",
        "summary": usage_tracker.get_summary(),
        "recent": usage_tracker.get_recent(limit=10),
    })


@tool("proxy_cost", "Return detailed cost breakdown by provider.", {})
async def proxy_cost(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.services.usage_tracker import usage_tracker
    except ImportError:
        return sdk_error("ai_proxy not available")

    summary = usage_tracker.get_summary()
    return sdk_result({
        "status": "success",
        "total_cost_usd": summary["total_cost_usd"],
        "total_tokens": summary["total_tokens"],
        "by_provider": summary["by_provider"],
    })


@tool(
    "simulate_route",
    "Dry-run route simulation — shows which provider/model would be selected without executing.",
    {
        "model": {"type": "string", "default": "gpt-4o-mini"},
        "prefer_free": {"type": "boolean", "default": False},
        "max_cost_per_1k": {"type": "number", "nullable": True},
    },
)
async def simulate_route(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.providers.registry import get_all_providers
        from ai_proxy.routing.combo import get_circuit_breaker_status, get_usage_counts, budget_guard
    except ImportError:
        return sdk_error("ai_proxy not available")

    model = args.get("model", "gpt-4o-mini")
    prefer_free = args.get("prefer_free", False)
    max_cost_per_1k = args.get("max_cost_per_1k")

    all_providers = get_all_providers()
    usage = get_usage_counts()
    cb_status = get_circuit_breaker_status()
    open_circuits = {cb["target"] for cb in cb_status if cb["state"] == "open"}

    candidates = []
    for p in all_providers.values():
        if not p.is_available:
            continue
        for m in p.models:
            if m.deprecated or (model and model != m.id):
                continue
            candidates.append({
                "provider": p.id, "model": m.id, "is_free": p.is_free,
                "cost_input": m.cost.input, "cost_output": m.cost.output,
                "context_window": m.context_window,
                "circuit_open": f"{p.id}:{m.id}" in open_circuits,
                "usage_count": usage.get(p.id, 0),
            })

    if prefer_free:
        candidates.sort(key=lambda c: (not c["is_free"], c["cost_input"]))
    elif max_cost_per_1k is not None:
        candidates = [c for c in candidates if c["cost_input"] <= max_cost_per_1k * 1000]
        candidates.sort(key=lambda c: c["cost_input"])
    else:
        candidates.sort(key=lambda c: c["cost_input"])

    selected = next((c for c in candidates if not c["circuit_open"]), None)
    return sdk_result({
        "status": "success", "selected": selected,
        "candidates_total": len(candidates),
        "candidates_available": sum(1 for c in candidates if not c["circuit_open"]),
        "open_circuits": len(open_circuits), "budget": budget_guard.get_all(),
    })


@tool(
    "set_budget_guard",
    "Set a spending budget guard for a combo or tier key.",
    {"key": "string", "budget_usd": "number"},
)
async def set_budget_guard(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.routing.combo import budget_guard
    except ImportError:
        return sdk_error("ai_proxy not available")

    key, budget_usd = args["key"], float(args["budget_usd"])
    current = budget_guard.get_spent(key)
    return sdk_result({
        "status": "success", "key": key, "budget_usd": budget_usd,
        "current_spent": current, "remaining": max(0.0, budget_usd - current),
    })


@tool("get_circuit_breakers", "Return circuit breaker status for all routing targets.", {})
async def get_circuit_breakers(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.routing.combo import get_circuit_breaker_status
    except ImportError:
        return sdk_error("ai_proxy not available")

    cb_status = get_circuit_breaker_status()
    open_count = sum(1 for cb in cb_status if cb["state"] == "open")
    return sdk_result({
        "status": "success", "circuit_breakers": cb_status,
        "total": len(cb_status), "open": open_count, "closed": len(cb_status) - open_count,
    })


@tool(
    "explain_route",
    "Explain step-by-step why a specific provider/model would be chosen for a request.",
    {"model": {"type": "string", "default": "gpt-4o-mini"}, "provider": {"type": "string", "nullable": True}},
)
async def explain_route(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.providers.registry import get_all_providers
        from ai_proxy.routing.combo import get_circuit_breaker_status, get_usage_counts
        from ai_proxy.services.rate_limiter import rate_limiter  # noqa: F401
    except ImportError:
        return sdk_error("ai_proxy not available")

    model = args.get("model", "gpt-4o-mini")
    provider = args.get("provider")
    steps: list[str] = []
    all_p = get_all_providers()
    usage = get_usage_counts()
    open_targets = {cb["target"] for cb in get_circuit_breaker_status() if cb["state"] == "open"}

    matching = [(p, m) for p in all_p.values() for m in p.models if m.id == model or not model]
    steps.append(f"1. Found {len(matching)} provider(s) offering model '{model}'")
    if provider:
        matching = [(p, m) for p, m in matching if p.id == provider]
        steps.append(f"2. Filtered to provider '{provider}': {len(matching)} match(es)")

    available = [(p, m) for p, m in matching if p.is_available]
    cb_blocked = [(p, m) for p, m in available if f"{p.id}:{m.id}" in open_targets]
    if cb_blocked:
        steps.append(f"3. {len(cb_blocked)} target(s) blocked by circuit breaker")
        available = [(p, m) for p, m in available if f"{p.id}:{m.id}" not in open_targets]
    available.sort(key=lambda pm: pm[1].cost.input)
    if available:
        p, m = available[0]
        steps.append(f"4. Selected: {p.id}/{m.id} (${m.cost.input}/M in, {usage.get(p.id, 0)} prior requests)")

    return sdk_result({
        "status": "success", "model": model, "provider": provider, "steps": steps,
        "selected": {"provider": available[0][0].id, "model": available[0][1].id} if available else None,
    })


@tool("routing_strategies", "List all available routing strategies with descriptions.", {})
async def routing_strategies(args: dict[str, Any]) -> JsonDict:
    try:
        from ai_proxy.routing.combo import Strategy
    except ImportError:
        return sdk_error("ai_proxy not available")

    strategies = [{"id": s.value, "name": s.name.replace("_", " ").title()} for s in Strategy]
    return sdk_result({"status": "success", "strategies": strategies, "count": len(strategies)})


ALL_TOOLS = [
    proxy_chat, proxy_providers, proxy_models, proxy_usage, proxy_cost,
    simulate_route, set_budget_guard, get_circuit_breakers, explain_route, routing_strategies,
]
