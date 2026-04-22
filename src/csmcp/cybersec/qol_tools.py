"""QoL Output Controls — MCP tool definitions.

4 tools:
    qol_get       — get current QoL settings for a scope
    qol_set       — enable/disable one or more toggles
    qol_reset     — reset all toggles for a scope
    qol_presets   — list available presets (builtin + user-defined)

Referenz:
    plan.md T006 — Phase 1 QoL Core
    src/ai_proxy/qol_controls/models.py   — QoLToggle, QoLSettings, BUILTIN_PRESETS
    src/ai_proxy/qol_controls/manager.py  — QoLManager
    src/csmcp/cybersec/tool_toggles.py    — design pattern
"""
from __future__ import annotations

from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error

_TOGGLE_VALUES = [
    "no_thinking",
    "no_chat",
    "minimal",
    "file_only",
    "no_markdown",
    "structured_only",
    "redact_secrets",
    "append_audit_trail",
]

_SCOPE_VALUES = ["session", "project", "global"]


def _manager():
    from ai_proxy.qol_controls.manager import get_manager
    return get_manager()


# ── qol_get ──────────────────────────────────────────────────────────────────

@tool(
    "qol_get",
    "Get current QoL output-control settings for a scope. "
    "Returns active toggles, preset name, token estimate, and a fragment preview.",
    {
        "scope": {
            "type": "string",
            "enum": _SCOPE_VALUES,
            "default": "session",
            "description": "Scope to query (session / project / global)",
        },
    },
)
async def qol_get(args: dict[str, Any]) -> JsonDict:
    scope = (args.get("scope") or "session").strip().lower()
    if scope not in _SCOPE_VALUES:
        return sdk_error(f"Invalid scope '{scope}'. Must be one of: {_SCOPE_VALUES}")
    return sdk_result(_manager().status(scope))


# ── qol_set ──────────────────────────────────────────────────────────────────

@tool(
    "qol_set",
    "Enable or disable QoL output-control toggles for a scope. "
    "You may also load a named preset (builtin: silent, code-only, structured, audit, plain-text).",
    {
        "scope": {
            "type": "string",
            "enum": _SCOPE_VALUES,
            "default": "session",
            "description": "Scope to modify",
        },
        "enable": {
            "type": "array",
            "items": {"type": "string", "enum": _TOGGLE_VALUES},
            "description": "Toggle names to activate",
        },
        "disable": {
            "type": "array",
            "items": {"type": "string", "enum": _TOGGLE_VALUES},
            "description": "Toggle names to deactivate",
        },
        "preset": {
            "type": "string",
            "description": "Load a named preset first, then apply enable/disable overrides",
        },
    },
)
async def qol_set(args: dict[str, Any]) -> JsonDict:
    scope = (args.get("scope") or "session").strip().lower()
    if scope not in _SCOPE_VALUES:
        return sdk_error(f"Invalid scope '{scope}'")

    mgr = _manager()
    settings = mgr.load_settings(scope)

    preset_name = (args.get("preset") or "").strip()
    if preset_name:
        preset = mgr.load_preset(preset_name)
        if preset is None:
            return sdk_error(
                f"Preset '{preset_name}' not found. "
                f"Available: {list(mgr.list_presets().keys())}"
            )
        settings.enabled_toggles = preset.enabled_toggles.copy()
        settings.preset_name = preset_name

    from ai_proxy.qol_controls.models import QoLToggle
    errors: list[str] = []

    for v in (args.get("enable") or []):
        try:
            settings.activate(QoLToggle(v))
        except ValueError:
            errors.append(f"Unknown toggle: {v!r}")

    for v in (args.get("disable") or []):
        try:
            settings.deactivate(QoLToggle(v))
        except ValueError:
            errors.append(f"Unknown toggle: {v!r}")

    if errors:
        return sdk_error("; ".join(errors))

    mgr.save_settings(settings)
    return sdk_result({
        "message": "QoL settings updated",
        **mgr.status(scope),
    })


# ── qol_reset ────────────────────────────────────────────────────────────────

@tool(
    "qol_reset",
    "Reset all QoL output-control toggles for a scope back to defaults (all disabled).",
    {
        "scope": {
            "type": "string",
            "enum": _SCOPE_VALUES,
            "default": "session",
            "description": "Scope to reset",
        },
    },
)
async def qol_reset(args: dict[str, Any]) -> JsonDict:
    scope = (args.get("scope") or "session").strip().lower()
    if scope not in _SCOPE_VALUES:
        return sdk_error(f"Invalid scope '{scope}'")
    mgr = _manager()
    mgr.reset_settings(scope)
    return sdk_result({
        "message": f"QoL settings reset for scope '{scope}'",
        "scope": scope,
        "active_toggles": [],
    })


# ── qol_presets ──────────────────────────────────────────────────────────────

@tool(
    "qol_presets",
    "List all available QoL output-control presets (builtin + user-defined).",
    {},
)
async def qol_presets(args: dict[str, Any]) -> JsonDict:
    presets = _manager().list_presets()
    return sdk_result({
        "presets": {
            name: {
                "enabled_toggles": data.get("enabled_toggles", []),
                "source": data.get("source", "unknown"),
            }
            for name, data in presets.items()
        },
        "count": len(presets),
    })


ALL_TOOLS = [qol_get, qol_set, qol_reset, qol_presets]
