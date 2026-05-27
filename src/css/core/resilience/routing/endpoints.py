"""Admin REST endpoints for routing management."""

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from .budget import budget_guard
from .circuit_breaker import circuit_breaker
from .rate_limiter import rate_limiter
from .registry import combo_registry
from .strategy import PROVIDER_TIER_LIST
from .usage_tracker import usage_tracker

router = APIRouter(prefix="/routing", tags=["routing"])


async def require_admin(request: Request) -> None:
    user = getattr(request.state, "user", None)
    is_admin = getattr(user, "is_admin", None) if user is not None else None
    if is_admin is not True:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/combos")
async def list_combos(request: Request) -> list[dict[str, Any]]:
    await require_admin(request)
    return [_combo_to_dict(c) for c in combo_registry.list_all()]


@router.get("/combos/{combo_id}")
async def get_combo(request: Request, combo_id: str) -> dict[str, Any]:
    await require_admin(request)
    combo = combo_registry.get(combo_id)
    if combo is None:
        raise HTTPException(status_code=404, detail="Combo not found")
    return _combo_to_dict(combo)


@router.put("/combos/{combo_id}")
async def upsert_combo(request: Request, combo_id: str) -> dict[str, str]:
    await require_admin(request)
    combo_registry.invalidate(combo_id)
    return {"status": "invalidated", "combo_id": combo_id}


@router.get("/circuit-breakers")
async def list_circuit_breakers(request: Request) -> dict[str, dict[str, int | float | bool]]:
    await require_admin(request)
    return circuit_breaker.get_all()


@router.post("/circuit-breakers/{target}/reset")
async def reset_circuit_breaker(request: Request, target: str) -> dict[str, str]:
    await require_admin(request)
    circuit_breaker.reset(target)
    return {"status": "reset", "target": target}


@router.get("/budget")
async def list_budget(request: Request) -> dict[str, float]:
    await require_admin(request)
    return budget_guard.get_all()


@router.post("/budget/{combo_id}/reset")
async def reset_budget(request: Request, combo_id: str) -> dict[str, str]:
    await require_admin(request)
    budget_guard.reset(combo_id)
    return {"status": "reset", "combo_id": combo_id}


@router.get("/tiers")
async def list_tiers(request: Request) -> list[dict[str, Any]]:
    await require_admin(request)
    return [
        {
            "name": t.name,
            "rank": t.rank,
            "models": t.representative_models,
            "complexity_ceiling": t.complexity_ceiling,
            "runtime": t.runtime,
            "min_vram_gb": t.min_vram_gb,
            "input_cost_per_mtok": t.input_cost_per_mtok,
            "output_cost_per_mtok": t.output_cost_per_mtok,
            "is_terminal": t.is_terminal,
        }
        for t in PROVIDER_TIER_LIST
    ]


@router.get("/rate-limits")
async def get_rate_limits(request: Request) -> dict[str, dict[str, float | int | bool]]:
    await require_admin(request)
    return rate_limiter.get_status()


@router.get("/usage")
async def get_usage(request: Request, limit: int = 50) -> dict[str, Any]:
    await require_admin(request)
    recent = usage_tracker.get_recent(limit)
    summary = usage_tracker.get_summary()
    return {
        "summary": summary,
        "recent": [
            {
                "provider_id": r.provider_id,
                "model_id": r.model_id,
                "prompt_tokens": r.prompt_tokens,
                "completion_tokens": r.completion_tokens,
                "cost_usd": r.cost_usd,
                "latency_ms": r.latency_ms,
                "stream": r.stream,
                "success": r.success,
                "error": r.error,
            }
            for r in recent
        ],
    }


def _combo_to_dict(combo: Any) -> dict[str, Any]:
    return {
        "id": combo.id,
        "name": combo.name,
        "strategy": combo.strategy.value if hasattr(combo.strategy, "value") else combo.strategy,
        "targets": [
            {
                "provider_id": t.provider_id,
                "model_id": t.model_id,
                "weight": t.weight,
                "enabled": t.enabled,
            }
            for t in combo.targets
        ],
        "budget_usd": combo.budget_usd,
        "description": combo.description,
        "tags": combo.tags,
    }
