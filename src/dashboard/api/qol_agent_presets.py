"""API endpoints for per-agent QoL presets (T018).

Provides REST endpoints to bind and manage QoL presets per agent:
    GET    /api/qol/agent/{agent_id}/preset      — get bound preset
    POST   /api/qol/agent/{agent_id}/preset      — bind preset to agent
    DELETE /api/qol/agent/{agent_id}/preset      — unbind preset from agent

Thread-safe, async, with proper error handling.
"""
from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


def _manager():
    from ai_proxy.qol_controls.manager import get_manager
    return get_manager()


def _publisher():
    from ai_proxy.qol_controls.a2a_integration import get_publisher
    return get_publisher()


async def api_qol_agent_preset_get(request: Request) -> JSONResponse:
    """GET /api/qol/agent/{agent_id}/preset — get bound preset for agent (T018)."""
    agent_id = request.path_params.get("agent_id", "").strip()
    if not agent_id:
        return JSONResponse({"error": "Agent ID required"}, status_code=400)

    try:
        mgr = _manager()
        preset_name = mgr.get_agent_preset(agent_id)
        if not preset_name:
            return JSONResponse(
                {"preset": None, "agent": agent_id},
                status_code=200,
            )

        preset = mgr.load_preset(preset_name)
        if not preset:
            return JSONResponse(
                {"error": f"Preset '{preset_name}' not found"},
                status_code=404,
            )

        return JSONResponse({
            "agent": agent_id,
            "preset": preset_name,
            "toggles": [t.value for t in sorted(preset.enabled_toggles, key=lambda x: x.value)],
        })
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


async def api_qol_agent_preset_post(request: Request) -> JSONResponse:
    """POST /api/qol/agent/{agent_id}/preset — bind preset to agent (T017/T018)."""
    agent_id = request.path_params.get("agent_id", "").strip()
    if not agent_id:
        return JSONResponse({"error": "Agent ID required"}, status_code=400)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    preset_name = (body.get("preset") or "").strip()
    if not preset_name:
        return JSONResponse({"error": "Preset name required"}, status_code=400)

    try:
        mgr = _manager()
        # Validate preset exists
        preset = mgr.load_preset(preset_name)
        if not preset:
            available = list(mgr.list_presets().keys())
            return JSONResponse(
                {"error": f"Preset '{preset_name}' not found", "available": available},
                status_code=404,
            )

        # Validate combo (T019)
        from ai_proxy.qol_controls.models import QoLSecurityError
        try:
            mgr.set_agent_preset(agent_id, preset_name)
        except QoLSecurityError as e:
            return JSONResponse(
                {"error": f"Security violation: {str(e)}"},
                status_code=409,
            )

        # T017: publish preset binding via A2A
        import asyncio
        publisher = _publisher()
        asyncio.create_task(publisher.publish_preset_bound(agent_id, preset_name))

        return JSONResponse({
            "ok": True,
            "agent": agent_id,
            "preset": preset_name,
            "toggles": [t.value for t in sorted(preset.enabled_toggles, key=lambda x: x.value)],
        })
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


async def api_qol_agent_preset_delete(request: Request) -> JSONResponse:
    """DELETE /api/qol/agent/{agent_id}/preset — unbind preset from agent (T017/T018)."""
    agent_id = request.path_params.get("agent_id", "").strip()
    if not agent_id:
        return JSONResponse({"error": "Agent ID required"}, status_code=400)

    try:
        mgr = _manager()
        mgr.set_agent_preset(agent_id, None)

        # T017: publish unbinding via A2A
        import asyncio
        publisher = _publisher()
        asyncio.create_task(publisher.publish_preset_bound(agent_id, ""))

        return JSONResponse({
            "ok": True,
            "agent": agent_id,
            "preset": None,
        })
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
