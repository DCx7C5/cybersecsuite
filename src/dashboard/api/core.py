"""Core dashboard API handlers: overview, providers, usage, health, crypto."""
from __future__ import annotations

import asyncio
import os
import time

import httpx
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
from db.models.provider import ProviderAuthMethod
from db.models.api_account import ApiAccount

_APP_START = time.monotonic()
_LAST_REQUEST_TIME = _APP_START  # Track last dashboard request
_PLUGIN_REGISTERED: dict[str, float] = {}  # Track plugin registrations by domain


async def api_dashboard_activity(request: Request) -> JSONResponse:
    """Check if dashboard is currently in use (activity in last 5 seconds).
    
    Used by browser plugin to detect if streaming should be blocked.
    Returns: { "active": bool, "idle_seconds": float }
    """
    global _LAST_REQUEST_TIME
    now = time.monotonic()
    idle = now - _LAST_REQUEST_TIME
    active = idle < 5.0  # Consider active if request in last 5 seconds
    
    return JSONResponse({"active": active, "idle_seconds": idle})


async def api_plugin_register(request: Request) -> JSONResponse:
    """Plugin registers itself as active from browser.
    
    Called by plugin on startup to notify dashboard of its presence.
    Returns: { "ok": bool, "dashboard_version": str }
    """
    global _PLUGIN_REGISTERED
    now = time.monotonic()
    
    try:
        body = await request.json()
        domain = body.get("domain", "unknown")
    except:
        domain = "unknown"
    
    _PLUGIN_REGISTERED[domain] = now
    return JSONResponse({"ok": True, "dashboard_version": "3.0", "registered_at": now})


async def api_plugin_status(request: Request) -> JSONResponse:
    """Check if any plugin is currently active in browser.
    
    Dashboard calls this on startup/periodically to detect plugin presence.
    Returns: { "active": bool, "plugins": { domain: last_registered_time }, "uptime_seconds": float }
    """
    global _PLUGIN_REGISTERED
    now = time.monotonic()
    
    # Consider plugins active if registered in last 30 seconds
    active_plugins = {
        domain: (now - ts) 
        for domain, ts in _PLUGIN_REGISTERED.items() 
        if (now - ts) < 30
    }
    
    return JSONResponse({
        "active": len(active_plugins) > 0,
        "plugins": active_plugins,
        "uptime_seconds": now - _APP_START,
    })


def _record_dashboard_activity():
    """Record that dashboard had activity (called on every request)."""
    global _LAST_REQUEST_TIME
    _LAST_REQUEST_TIME = time.monotonic()


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
        "uptime_seconds": round(time.monotonic() - _APP_START, 1),
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


async def api_providers_hub(request: Request) -> JSONResponse:
    """Aggregated provider hub: registry + DB auth methods + DB accounts."""
    # Fetch DB records with graceful fallback
    auth_methods_by_provider: dict[str, list[dict]] = {}
    accounts_by_provider: dict[str, list[dict]] = {}
    try:
        db_auth_methods = await asyncio.wait_for(
            ProviderAuthMethod.all().select_related("provider"),
            timeout=5.0,
        )
        for am in db_auth_methods:
            pid = am.provider_id
            auth_methods_by_provider.setdefault(pid, []).append({
                "auth_method": am.auth_method,
                "config": am.config or {},
            })
    except Exception:
        pass

    try:
        db_accounts = await asyncio.wait_for(
            ApiAccount.all().select_related("provider"),
            timeout=5.0,
        )
        for acc in db_accounts:
            pid = acc.provider_id
            accounts_by_provider.setdefault(pid, []).append({
                "vault_key": acc.vault_key,
                "label": acc.label,
                "auth_method": acc.auth_method,
                "email": acc.email,
                "display_name": acc.display_name,
                "subject": acc.subject,
                "tenant": acc.tenant,
                "active": acc.active,
                "test_status": acc.test_status,
            })
    except Exception:
        pass

    result = []
    for p in get_all_providers().values():
        status = "available" if p.is_available else "no_credentials"
        if not p.enabled:
            status = "disabled"

        result.append({
            "id": p.id,
            "name": p.name,
            "base_url": p.base_url,
            "status": status,
            "is_free": p.is_free,
            "auth_type": p.auth_type.value,
            "models_count": len([m for m in p.models if not m.deprecated]),
            "auth_methods": auth_methods_by_provider.get(p.id, []),
            "accounts": accounts_by_provider.get(p.id, []),
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
    """Combined health: DB + Redis + OpenObserve + proxy."""
    # DB health with timeout
    try:
        from db.bootstrap import get_database_health_async
        db_health = await asyncio.wait_for(
            get_database_health_async(check_connection=True, include_counts=False),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        db_health = {"status": "error", "error": "health check timed out"}
    except Exception as e:
        db_health = {"status": "error", "error": str(e)}

    # Redis health
    redis_health: dict = {"status": "unknown"}
    try:
        import redis.asyncio as aioredis
        redis_url = os.environ.get("CYBERSEC_REDIS_URL", "redis://localhost:6379/0")
        r = aioredis.from_url(redis_url, socket_connect_timeout=3)
        pong = await asyncio.wait_for(r.ping(), timeout=3.0)
        redis_health = {"status": "ok" if pong else "error"}
        info = await r.info(section="memory")
        redis_health["used_memory_human"] = info.get("used_memory_human", "?")
        await r.aclose()
    except Exception as e:
        redis_health = {"status": "error", "error": str(e)}

    # OpenObserve health
    oo_health: dict = {"status": "unknown"}
    try:
        oo_url = os.environ.get("OPENOBSERVE_HOST", os.environ.get("CYBERSEC_OPENOBSERVE_URL", "http://localhost:5080"))
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{oo_url}/healthz")
            oo_health = {"status": "ok" if resp.status_code == 200 else "degraded",
                         "http_status": resp.status_code}
    except Exception as e:
        oo_health = {"status": "error", "error": str(e)}

    # Local LLM providers
    local_providers = []
    for pid in ("ollama", "lmstudio"):
        from ai_proxy.providers.registry import get_provider
        p = get_provider(pid)
        if p and p.enabled:
            reachable = False
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    resp = await client.get(f"{p.base_url.rstrip('/')}/models")
                    reachable = resp.status_code == 200
            except Exception:
                pass
            local_providers.append({"id": pid, "name": p.name, "reachable": reachable})

    enabled = get_enabled_providers()
    return JSONResponse({
        "database": db_health,
        "redis": redis_health,
        "openobserve": oo_health,
        "proxy": {
            "providers_enabled": len(enabled),
            "providers_free": len(get_free_providers()),
            "uptime_seconds": round(time.monotonic() - _APP_START, 1),
        },
        "local_llm": local_providers,
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


# In-process active local model (survives until container restart)
_active_local_model: str | None = None


async def api_local_llm_status(request: Request) -> JSONResponse:
    """GET /api/local-llm/status — check local LLM provider reachability + models."""
    from ai_proxy.providers.registry import get_provider
    results = []
    for pid in ("ollama", "lmstudio"):
        p = get_provider(pid)
        if not p or not p.enabled:
            continue
        info: dict = {"id": pid, "name": p.name, "base_url": p.base_url,
                      "reachable": False, "models": []}
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{p.base_url.rstrip('/')}/models")
                if resp.status_code == 200:
                    info["reachable"] = True
                    data = resp.json()
                    if isinstance(data, dict) and "data" in data:
                        info["models"] = [m.get("id", "") for m in data["data"] if isinstance(m, dict)]
                    elif isinstance(data, dict) and "models" in data:
                        info["models"] = [m.get("name", "") for m in data["models"] if isinstance(m, dict)]
        except Exception:
            pass
        results.append(info)

    return JSONResponse({
        "providers": results,
        "active_model": _active_local_model,
        "default_model": os.environ.get("CYBERSEC_DEFAULT_MODEL", ""),
    })


async def api_local_llm_activate(request: Request) -> JSONResponse:
    """POST /api/local-llm/activate — set the default model to a local LLM model."""
    global _active_local_model
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "error": "invalid JSON"}, status_code=400)

    model_id = (body.get("model") or "").strip()
    if not model_id:
        # Deactivate — revert to cloud default
        _active_local_model = None
        os.environ.pop("CYBERSEC_DEFAULT_MODEL", None)
        return JSONResponse({"status": "ok", "active_model": None, "message": "Reverted to cloud default"})

    # Verify the model is reachable
    from ai_proxy.providers.registry import get_provider
    reachable = False
    for pid in ("ollama", "lmstudio"):
        p = get_provider(pid)
        if not p or not p.enabled:
            continue
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{p.base_url.rstrip('/')}/models")
                if resp.status_code == 200:
                    reachable = True
                    break
        except Exception:
            continue

    if not reachable:
        return JSONResponse({"status": "error", "error": "no local LLM provider reachable"}, status_code=503)

    _active_local_model = model_id
    os.environ["CYBERSEC_DEFAULT_MODEL"] = model_id
    return JSONResponse({"status": "ok", "active_model": model_id})
