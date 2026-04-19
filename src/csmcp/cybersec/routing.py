"""Routing and combo management tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


@tool("combo_list", "List all configured combos (model chains) with strategies + optional metrics.", {})
async def combo_list(args: dict[str, Any]) -> JsonDict:
    # Stub: return sample combos
    combos = [
        {
            "id": "default",
            "name": "Default Fallback",
            "strategy": "priority",
            "targets": [
                {"provider": "openai", "model": "gpt-4o", "weight": 1.0},
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "weight": 0.8},
            ],
            "metrics": {"requests": 150, "success_rate": 0.95, "avg_latency_ms": 1200},
        },
        {
            "id": "cost-optimized",
            "name": "Cost Optimized",
            "strategy": "cost_optimized",
            "targets": [
                {"provider": "openai", "model": "gpt-4o-mini", "weight": 1.0},
                {"provider": "anthropic", "model": "claude-3-5-haiku-20241022", "weight": 0.9},
            ],
            "metrics": {"requests": 75, "success_rate": 0.98, "avg_latency_ms": 800},
        },
    ]
    return sdk_result({"status": "success", "combos": combos, "count": len(combos)})


@tool("combo_metrics", "Detailed performance metrics for a specific combo.", {"combo_id": "string"})
async def combo_metrics(args: dict[str, Any]) -> JsonDict:
    combo_id = args.get("combo_id", "default")
    # Stub: return sample metrics
    metrics = {
        "combo_id": combo_id,
        "total_requests": 150,
        "successful_requests": 142,
        "failed_requests": 8,
        "success_rate": 0.9467,
        "avg_latency_ms": 1200,
        "p95_latency_ms": 2500,
        "p99_latency_ms": 4000,
        "cost_total_usd": 12.45,
        "cost_per_request_usd": 0.083,
        "provider_breakdown": {
            "openai": {"requests": 120, "success_rate": 0.95, "avg_latency_ms": 1100},
            "anthropic": {"requests": 30, "success_rate": 0.93, "avg_latency_ms": 1400},
        },
        "circuit_breaker_events": 2,
        "rate_limit_hits": 5,
    }
    return sdk_result({"status": "success", "metrics": metrics})


@tool("combo_switch", "Activate or deactivate a combo for routing.", {"combo_id": "string", "enabled": "boolean"})
async def combo_switch(args: dict[str, Any]) -> JsonDict:
    combo_id = args.get("combo_id")
    enabled = args.get("enabled", True)
    if not combo_id:
        return sdk_error("combo_id is required")
    # Stub: simulate switching
    return sdk_result({
        "status": "success",
        "combo_id": combo_id,
        "enabled": enabled,
        "message": f"Combo '{combo_id}' {'enabled' if enabled else 'disabled'}",
    })


@tool("combo_test", "Live-test each provider in a combo: latency, cost, success per provider.", {"combo_id": "string"})
async def combo_test(args: dict[str, Any]) -> JsonDict:
    combo_id = args.get("combo_id", "default")
    # Stub: simulate testing
    test_results = [
        {
            "provider": "openai",
            "model": "gpt-4o",
            "success": True,
            "latency_ms": 1150,
            "cost_usd": 0.012,
            "error": None,
        },
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "success": True,
            "latency_ms": 1320,
            "cost_usd": 0.015,
            "error": None,
        },
    ]
    return sdk_result({
        "status": "success",
        "combo_id": combo_id,
        "test_results": test_results,
        "overall_success": all(r["success"] for r in test_results),
    })


@tool("route_request", "Send chat completion through OmniRoute intelligent routing.", {"prompt": "string", "model": {"type": "string", "nullable": True}})
async def route_request(args: dict[str, Any]) -> JsonDict:
    prompt = args.get("prompt", "")
    model = args.get("model")
    if not prompt.strip():
        return sdk_error("prompt is required")
    # Stub: simulate routing
    return sdk_result({
        "status": "success",
        "content": f"Simulated response to: {prompt[:50]}...",
        "provider": "openai",
        "model": model or "gpt-4o",
        "latency_ms": 1200,
        "usage": {"input_tokens": 150, "output_tokens": 200, "total_tokens": 350},
    })


@tool("simulate_route", "Dry-run routing simulation: path, probabilities, costs, circuit breakers.", {"model": {"type": "string", "nullable": True}})
async def simulate_route(args: dict[str, Any]) -> JsonDict:
    model = args.get("model", "gpt-4o")
    # Stub: simulate routing decision
    simulation = {
        "model": model,
        "selected_path": {"provider": "openai", "model": "gpt-4o", "reason": "lowest cost"},
        "probabilities": [
            {"provider": "openai", "model": "gpt-4o", "probability": 0.7, "cost_usd": 0.012},
            {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "probability": 0.3, "cost_usd": 0.015},
        ],
        "circuit_breakers": {"open": [], "closed": ["openai:gpt-4o", "anthropic:claude-3-5-sonnet-20241022"]},
        "budget_status": {"remaining_usd": 45.50, "total_budget_usd": 50.00},
    }
    return sdk_result({"status": "success", "simulation": simulation})


@tool("set_routing_strategy", "Update combo routing strategy at runtime (priority/weighted/round-robin/auto).", {"combo_id": "string", "strategy": "string"})
async def set_routing_strategy(args: dict[str, Any]) -> JsonDict:
    combo_id = args.get("combo_id", "default")
    strategy = args.get("strategy", "priority")
    valid_strategies = ["priority", "weighted", "round_robin", "auto", "cost_optimized"]
    if strategy not in valid_strategies:
        return sdk_error(f"Invalid strategy. Valid: {', '.join(valid_strategies)}")
    # Stub: simulate setting
    return sdk_result({
        "status": "success",
        "combo_id": combo_id,
        "strategy": strategy,
        "message": f"Routing strategy for '{combo_id}' set to '{strategy}'",
    })


@tool("set_resilience_profile", "Apply resilience profile: circuit breakers, retries, timeouts, fallback depth.", {"profile": "string"})
async def set_resilience_profile(args: dict[str, Any]) -> JsonDict:
    profile = args.get("profile", "default")
    profiles = {
        "default": {"circuit_breaker_threshold": 5, "retry_count": 3, "timeout_sec": 30, "fallback_depth": 2},
        "aggressive": {"circuit_breaker_threshold": 3, "retry_count": 5, "timeout_sec": 15, "fallback_depth": 3},
        "conservative": {"circuit_breaker_threshold": 10, "retry_count": 1, "timeout_sec": 60, "fallback_depth": 1},
    }
    if profile not in profiles:
        return sdk_error(f"Invalid profile. Valid: {', '.join(profiles.keys())}")
    # Stub: simulate setting
    return sdk_result({
        "status": "success",
        "profile": profile,
        "settings": profiles[profile],
        "message": f"Resilience profile set to '{profile}'",
    })


@tool("best_combo_for_task", "Recommend best combo for a task type (fitness, cost, latency constraints).", {"task_type": "string", "constraints": {"type": "object", "nullable": True}})
async def best_combo_for_task(args: dict[str, Any]) -> JsonDict:
    task_type = args.get("task_type", "general")
    constraints = args.get("constraints", {})
    # Stub: recommend based on task type
    recommendations = {
        "coding": {"combo_id": "cost-optimized", "reason": "Lower cost for code generation", "fitness_score": 0.85},
        "analysis": {"combo_id": "default", "reason": "Higher quality for complex analysis", "fitness_score": 0.92},
        "general": {"combo_id": "default", "reason": "Balanced performance", "fitness_score": 0.78},
    }
    rec = recommendations.get(task_type, recommendations["general"])
    return sdk_result({"status": "success", "recommendation": rec, "task_type": task_type, "constraints": constraints})


@tool("explain_route", "Explain why a request was routed to a specific provider (scoring factors).", {"model": {"type": "string", "nullable": True}})
async def explain_route(args: dict[str, Any]) -> JsonDict:
    model = args.get("model", "gpt-4o")
    # Stub: explain routing decision
    explanation = {
        "model": model,
        "selected_provider": "openai",
        "selected_model": "gpt-4o",
        "scoring_factors": [
            {"factor": "cost", "score": 0.9, "weight": 0.4, "reason": "Lowest input cost at $0.0015/1K tokens"},
            {"factor": "latency", "score": 0.8, "weight": 0.3, "reason": "Historical avg 1.2s response time"},
            {"factor": "availability", "score": 1.0, "weight": 0.2, "reason": "Provider online, no circuit breaker"},
            {"factor": "quota", "score": 0.95, "weight": 0.1, "reason": "95% quota remaining"},
        ],
        "total_score": 0.885,
        "alternatives_considered": [
            {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "score": 0.82, "reason": "Higher cost"},
        ],
    }
    return sdk_result({"status": "success", "explanation": explanation})


ALL_TOOLS = [
    combo_list, combo_metrics, combo_switch, combo_test, route_request, simulate_route,
    set_routing_strategy, set_resilience_profile, best_combo_for_task, explain_route,
]
