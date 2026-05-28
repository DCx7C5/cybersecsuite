"""QoL admin REST endpoints for settings/presets/bindings."""

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from css.core.settings.qol import QoLToggle, toggle_description, validate_toggle_combo
from css.core.base.qol_registry import qol_preset_registry
from css.core.base.qol_settings import QoLSettingsManager

router = APIRouter(prefix="/api/qol", tags=["qol"])

_settings_mgr = QoLSettingsManager()


async def _require_user(request: Request) -> str:
    user = getattr(request.state, "user", None)
    user_id = str(getattr(user, "id", "")) if user is not None else ""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


@router.get("/toggles")
async def list_toggles(request: Request) -> list[dict[str, str]]:
    return [
        {"value": t.value, "description": toggle_description(t)}
        for t in QoLToggle
    ]


@router.get("/settings/{scope}")
async def get_settings(
    request: Request,
    scope: str,
    scope_id: str | None = None,
) -> dict[str, Any]:
    user_id = await _require_user(request)
    settings = await _settings_mgr.get_for_scope(user_id=user_id, scope=scope, scope_id=scope_id)
    if settings is None:
        return {"enabled_toggles": [], "scope": scope, "preset_name": None}
    return settings.as_dict()


@router.put("/settings/{scope}")
async def put_settings(
    request: Request,
    scope: str,
    payload: dict[str, Any],
    scope_id: str | None = None,
) -> dict[str, str]:
    user_id = await _require_user(request)
    from css.core.settings.qol import QoLSettings
    settings = QoLSettings.from_dict({**payload, "scope": scope})
    validate_toggle_combo(settings.enabled_toggles)
    await _settings_mgr.save_settings(
        user_id=user_id,
        scope=scope,
        scope_id=scope_id,
        settings=settings,
    )
    return {"status": "saved", "scope": scope}


@router.get("/presets")
async def list_presets(request: Request) -> list[dict[str, Any]]:
    await _require_user(request)
    all_presets = await qol_preset_registry.list_all()
    return [p.as_dict() for p in all_presets.values()]


@router.get("/presets/{name}")
async def get_preset(request: Request, name: str) -> dict[str, Any]:
    await _require_user(request)
    preset = await qol_preset_registry.get(name)
    if preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset.as_dict()


@router.put("/presets/{name}")
async def upsert_preset(request: Request, name: str, payload: dict[str, Any]) -> dict[str, str]:
    await _require_user(request)
    from css.core.settings.qol import QoLSettings
    settings = QoLSettings.from_dict({**payload, "scope": "preset", "preset_name": name})
    validate_toggle_combo(settings.enabled_toggles)
    user_id = request.state.user.id if hasattr(request.state, "user") and request.state.user else ""
    await qol_preset_registry.invalidate(user_id)
    return {"status": "upserted", "preset_name": name}


@router.delete("/presets/{name}")
async def delete_preset(request: Request, name: str) -> dict[str, str]:
    await _require_user(request)
    user_id = request.state.user.id if hasattr(request.state, "user") and request.state.user else ""
    await qol_preset_registry.invalidate(user_id)
    return {"status": "deleted", "preset_name": name}


@router.put("/bindings/{agent_name}")
async def set_binding(
    request: Request,
    agent_name: str,
    payload: dict[str, str],
) -> dict[str, str]:
    await _require_user(request)
    preset_name = payload.get("preset_name", "")
    if not preset_name:
        raise HTTPException(status_code=422, detail="preset_name is required")
    preset = await qol_preset_registry.get(preset_name)
    if preset is None:
        raise HTTPException(status_code=404, detail="Preset not found")
    user_id = request.state.user.id if hasattr(request.state, "user") and request.state.user else ""
    await qol_preset_registry.bind_agent_preset(
        user_id=user_id,
        agent_id=agent_name,
        preset_name=preset_name,
    )
    return {"status": "bound", "agent_name": agent_name, "preset_name": preset_name}


@router.delete("/bindings/{agent_name}")
async def remove_binding(request: Request, agent_name: str) -> dict[str, str]:
    await _require_user(request)
    user_id = request.state.user.id if hasattr(request.state, "user") and request.state.user else ""
    await qol_preset_registry.unbind_agent_preset(user_id=user_id, agent_id=agent_name)
    return {"status": "unbound", "agent_name": agent_name}


@router.get("/bindings")
async def list_bindings(request: Request) -> dict[str, str]:
    await _require_user(request)
    user_id = request.state.user.id if hasattr(request.state, "user") and request.state.user else ""
    return await qol_preset_registry.list_bindings(user_id=user_id)


@router.get("/status")
async def qol_status(request: Request) -> dict[str, object]:
    await _require_user(request)
    toggle_count = len(QoLToggle)
    all_presets = await qol_preset_registry.list_all()
    return {
        "toggle_count": toggle_count,
        "preset_count": len(all_presets),
        "toggles": [t.value for t in QoLToggle],
        "preset_names": list(all_presets.keys()),
    }
