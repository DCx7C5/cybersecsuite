"""Core dashboard API handlers: overview, providers, usage, health, crypto."""
from __future__ import annotations

import time

from starlette.requests import Request
from starlette.responses import JSONResponse

from ai_proxy.providers.registry import (
    AuthType,
    get_all_providers,
    get_browser_providers,
    get_enabled_providers,
    get_free_providers,
    list_all_models,
)
from ai_proxy.routing.combo import (
    Strategy,
    budget_guard,
    get_circuit_breaker_status,
    get_usage_counts,
)
from ai_proxy.services.rate_limiter import rate_limiter
from ai_proxy.services.usage_tracker import usage_tracker


async def api_overview(request: Request) -> JSONResponse:
    """Dashboard overview data."""
    all_p = get_all_providers()
    enabled = get_enabled_providers()
    free = get_free_providers()
    browser = get_browser_providers()
    models = list_all_models()
    summary = usage_tracker.get_summary()

    # Classify providers by tier
    tier_counts: dict[str, int] = {"free": 0, "budget": 0, "standard": 0, "premium": 0}
    for p in all_p.values():
        if p.is_free or p.auth_type in (AuthType.NONE, AuthType.BROWSER):
            tier_counts["free"] += 1
        elif p.models:
            avg = sum((m.cost.input + m.cost.output) / 2 for m in p.models) / len(p.models)
            if avg < 1.0:
                tier_counts["budget"] += 1
            elif avg <= 5.0:
                tier_counts["standard"] += 1
            else:
                tier_counts["premium"] += 1

    # Circuit breaker status
    cb_status = get_circuit_breaker_status()
    open_circuits = sum(1 for cb in cb_status if cb["state"] == "open")

    return JSONResponse({
        "providers": {"total": len(all_p), "enabled": len(enabled), "free": len(free), "browser": len(browser)},
        "models": {"total": len(models)},
        "tiers": tier_counts,
        "usage": summary,
        "budget": budget_guard.get_all(),
        "circuits": {"total": len(cb_status), "open": open_circuits},
        "strategies": [s.value for s in Strategy],
        "uptime_seconds": time.monotonic(),
    })


async def api_providers(request: Request) -> JSONResponse:
    """All providers with status, models, rate limits."""
    result = []
    for p in get_all_providers().values():
        status = "available" if p.is_available else "no_credentials"
        if not p.enabled:
            status = "disabled"

        rl = rate_limiter.get_status(p.id) if p.is_available else {}

        result.append({
            "id": p.id,
            "name": p.name,
            "status": status,
            "auth_type": p.auth_type.value,
            "api_format": p.api_format.value,
            "is_free": p.is_free,
            "base_url": p.base_url,
            "models": [
                {"id": m.id, "name": m.name, "context": m.context_window,
                 "cost_in": m.cost.input, "cost_out": m.cost.output,
                 "tools": m.supports_tools, "vision": m.supports_vision}
                for m in p.models if not m.deprecated
            ],
            "rate_limit": rl,
            "usage": get_usage_counts().get(p.id, 0),
        })
    return JSONResponse(result)


async def api_usage(request: Request) -> JSONResponse:
    """Usage history and cost analytics."""
    return JSONResponse({
        "summary": usage_tracker.get_summary(),
        "recent": usage_tracker.get_recent(limit=50),
        "rate_limits": rate_limiter.get_all_status(),
        "budget": budget_guard.get_all(),
    })


async def api_health(request: Request) -> JSONResponse:
    """Combined health: DB + proxy + providers."""
    try:
        from db.bootstrap import get_database_health_async
        db_health = await get_database_health_async(check_connection=True, include_counts=False)
    except Exception as e:
        db_health = {"status": "error", "error": str(e)}

    enabled = get_enabled_providers()
    return JSONResponse({
        "database": db_health,
        "proxy": {
            "providers_enabled": len(enabled),
            "providers_free": len(get_free_providers()),
            "uptime_seconds": round(time.monotonic(), 1),
        },
    })


async def api_crypto(request: Request) -> JSONResponse:
    """Crypto/artifact signing stats via Tortoise ORM."""
    try:
        from db.models.artifact import Artifact, ArtifactSignatureLog
        total_artifacts = await Artifact.all().count()
        valid_artifacts = await Artifact.filter(signature_valid=True).count()
        invalid_artifacts = await Artifact.filter(signature_valid=False).count()
        recent_sigs = await ArtifactSignatureLog.all().order_by(
            "-created_at"
        ).limit(10).prefetch_related("artifact")
        recent_logs = [
            {
                "artifact_id": log.artifact.id if log.artifact else None,
                "action": log.action,
                "status": log.verification_status,
                "key_id": log.key_id,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in recent_sigs
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})

    return JSONResponse({
        "total_artifacts": total_artifacts,
        "valid": valid_artifacts,
        "invalid": invalid_artifacts,
        "recent_signature_logs": recent_logs,
    })
