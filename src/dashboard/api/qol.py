"""QoL Output Controls — dashboard REST endpoints.

Routes:
    GET  /api/qol                  → current settings for a scope
    POST /api/qol                  → set / update toggles
    DELETE /api/qol                → reset toggles for a scope
    GET  /api/qol/presets          → list all presets
    POST /api/qol/presets/{name}   → save current settings as preset

Referenz:
    plan.md T008 — Phase 1 QoL Core
    src/ai_proxy/qol_controls/manager.py — QoLManager
    src/dashboard/api/settings_toggles.py — route pattern
"""
from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


def _manager():
    from ai_proxy.qol_controls.manager import get_manager
    return get_manager()


async def api_qol_get(request: Request) -> JSONResponse:
    """GET /api/qol?scope=session — get current QoL settings."""
    scope = request.query_params.get("scope", "session").strip().lower()
    if scope not in ("session", "project", "global"):
        return JSONResponse({"error": f"Invalid scope: {scope!r}"}, status_code=400)
    try:
        return JSONResponse(_manager().status(scope))
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


async def api_qol_post(request: Request) -> JSONResponse:
    """POST /api/qol — enable/disable toggles, optionally load a preset."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    scope = (body.get("scope") or "session").strip().lower()
    if scope not in ("session", "project", "global"):
        return JSONResponse({"error": f"Invalid scope: {scope!r}"}, status_code=400)

    mgr = _manager()
    settings = mgr.load_settings(scope)

    preset_name = (body.get("preset") or "").strip()
    if preset_name:
        preset = mgr.load_preset(preset_name)
        if preset is None:
            available = list(mgr.list_presets().keys())
            return JSONResponse(
                {"error": f"Preset '{preset_name}' not found", "available": available},
                status_code=404,
            )
        settings.enabled_toggles = preset.enabled_toggles.copy()
        settings.preset_name = preset_name

    from ai_proxy.qol_controls.models import QoLToggle

    for v in (body.get("enable") or []):
        try:
            settings.activate(QoLToggle(v))
        except ValueError:
            return JSONResponse({"error": f"Unknown toggle: {v!r}"}, status_code=400)

    for v in (body.get("disable") or []):
        try:
            settings.deactivate(QoLToggle(v))
        except ValueError:
            return JSONResponse({"error": f"Unknown toggle: {v!r}"}, status_code=400)

    mgr.save_settings(settings)
    return JSONResponse({"ok": True, **mgr.status(scope)})


async def api_qol_delete(request: Request) -> JSONResponse:
    """DELETE /api/qol?scope=session — reset all toggles for scope."""
    scope = request.query_params.get("scope", "session").strip().lower()
    if scope not in ("session", "project", "global"):
        return JSONResponse({"error": f"Invalid scope: {scope!r}"}, status_code=400)
    try:
        mgr = _manager()
        mgr.reset_settings(scope)
        return JSONResponse({"ok": True, "scope": scope, "active_toggles": []})
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


async def api_qol_presets_get(request: Request) -> JSONResponse:
    """GET /api/qol/presets — list all available presets."""
    try:
        presets = _manager().list_presets()
        return JSONResponse({"presets": presets, "count": len(presets)})
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


async def api_qol_preset_save(request: Request) -> JSONResponse:
    """POST /api/qol/presets/{name} — save current session settings as a named preset."""
    name = request.path_params.get("name", "").strip()
    if not name:
        return JSONResponse({"error": "Preset name is required"}, status_code=400)
    try:
        body = await request.json()
    except Exception:
        body = {}
    scope = (body.get("scope") or "session").strip().lower()
    mgr = _manager()
    settings = mgr.load_settings(scope)
    settings.preset_name = name
    mgr.save_preset(name, settings)
    return JSONResponse({"ok": True, "name": name, **settings.as_dict()})
