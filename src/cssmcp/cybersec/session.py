"""Session snapshot, agent registry, and best provider tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from cssmcp._sdk_compat import tool
from cssmcp.cybersec.helpers import JsonDict, _get_current_scope, sdk_result, sdk_error


@tool("session_snapshot", "Return a full session state snapshot including scope, usage, budget, and circuit breakers.", {})
async def session_snapshot(args: dict[str, Any]) -> JsonDict:
    try:
        from src.registries.providers import get_enabled_providers, get_free_providers
        from ai_proxy.routing.combo import get_circuit_breaker_status, get_usage_counts, budget_guard, Strategy
        from ai_proxy.services.usage_tracker import usage_tracker
    except ImportError:
        return sdk_error("ai_proxy not available")

    scope = _get_current_scope()
    cb_status = get_circuit_breaker_status()
    return sdk_result({
        "status": "success",
        "scope": scope,
        "providers": {"enabled": len(get_enabled_providers()), "free": len(get_free_providers())},
        "usage": usage_tracker.get_summary(),
        "usage_counts": get_usage_counts(),
        "budget": budget_guard.get_all(),
        "circuit_breakers": {
            "total": len(cb_status),
            "open": sum(1 for cb in cb_status if cb["state"] == "open"),
        },
        "strategies_available": [s.value for s in Strategy],
    })


@tool("agent_registry", "List all registered A2A agents with skills and metadata.", {})
async def agent_registry(args: dict[str, Any]) -> JsonDict:
    try:
        from src.registries.agents import AgentRegistry
        from a2a.agent_loader import load_cybersecsuite_agents

        registry = AgentRegistry()
        load_cybersecsuite_agents(registry)
        agents = registry.summary()
        orchestrators = [a for a in agents if a.get("claude_metadata", {}).get("role") == "orchestrator"]

        # Append installed marketplace agents (T036).
        try:
            from src.registries.marketplace import get_registry as _get_mkt_registry
            for item in _get_mkt_registry().list_installed():
                if item.kind == "agent":
                    agents.append({
                        "name": item.id,
                        "description": item.description,
                        "source": "marketplace",
                        "provider": item.provider,
                        "tags": item.tags,
                    })
        except Exception:
            pass  # marketplace not available — skip silently

        return sdk_result({
            "status": "success",
            "total": len(agents),
            "orchestrators": len(orchestrators),
            "specialists": len(agents) - len(orchestrators),
            "agents": agents,
        })
    except Exception as exc:
        return sdk_error(str(exc))


@tool(
    "best_provider",
    "Find the best provider/model for a task based on cost, capability, and circuit breaker state.",
    {
        "task": "string",
        "prefer_free": {"type": "boolean", "default": False},
        "max_cost_per_1k": {"type": "number", "nullable": True},
        "require_tools": {"type": "boolean", "default": False},
        "require_vision": {"type": "boolean", "default": False},
        "min_context": {"type": "integer", "nullable": True},
    },
)
async def best_provider(args: dict[str, Any]) -> JsonDict:
    try:
        from src.registries.providers import get_all_providers
        from ai_proxy.routing.combo import get_circuit_breaker_status
    except ImportError:
        return sdk_error("ai_proxy not available")

    prefer_free = args.get("prefer_free", False)
    max_cost_per_1k = args.get("max_cost_per_1k")
    require_tools = args.get("require_tools", False)
    require_vision = args.get("require_vision", False)
    min_context = args.get("min_context")

    open_targets = {cb["target"] for cb in get_circuit_breaker_status() if cb["state"] == "open"}
    candidates = []

    for p in get_all_providers().values():
        if not p.is_available:
            continue
        for m in p.models:
            if m.deprecated:
                continue
            if require_tools and not m.supports_tools:
                continue
            if require_vision and not m.supports_vision:
                continue
            if min_context and m.context_window < min_context:
                continue
            if max_cost_per_1k is not None and m.cost.input > max_cost_per_1k * 1000:
                continue
            if f"{p.id}:{m.id}" in open_targets:
                continue
            candidates.append({
                "provider": p.id, "model": m.id, "is_free": p.is_free,
                "cost_input": m.cost.input, "cost_output": m.cost.output,
                "context_window": m.context_window,
                "supports_tools": m.supports_tools, "supports_vision": m.supports_vision,
            })

    if prefer_free:
        candidates.sort(key=lambda c: (not c["is_free"], c["cost_input"]))
    else:
        candidates.sort(key=lambda c: c["cost_input"])

    return sdk_result({
        "status": "success",
        "task": args.get("task", ""),
        "best": candidates[0] if candidates else None,
        "candidates_count": len(candidates),
    })


ALL_TOOLS = [session_snapshot, agent_registry, best_provider]
