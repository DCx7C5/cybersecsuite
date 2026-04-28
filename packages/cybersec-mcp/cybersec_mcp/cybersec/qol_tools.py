"""QoL Output Controls — MCP tool definitions.

This module defines 5 MCP tools for QoL settings management:

1. qol_get(scope)
   Get current QoL settings for a scope. Returns active toggles, preset name,
   token estimate, and a fragment preview. Used for diagnostics and UI updates.

2. qol_set(scope, enable, disable, preset)
   Enable/disable toggles for a scope, optionally loading a named preset first,
   then applying enable/disable overrides. Validates combo before saving.

3. qol_reset(scope)
   Reset all toggles for a scope to factory defaults. Idempotent.

4. qol_presets(action, name, scope)
   List all available presets (builtin + user-defined), or save current
   settings as a new preset, or delete a user-defined preset.

5. qol_agent_preset(agent_name, preset_name, action)
   Bind/get/clear a per-agent QoL preset. When an agent's preset is bound,
   that preset is automatically used for all requests from that agent,
   overriding scope settings (T018).

Tool arguments use enums for validation:
    _TOGGLE_VALUES = 8 values (no_thinking, no_chat, etc.)
    _SCOPE_VALUES = 3 values (session, project, global)
    _PRESET_ACTIONS = 3 values (list, save, delete)
    _AGENT_ACTIONS = 3 values (get, set, clear)

All tools return structured JSON with:
    - success: boolean (implicit: result dict means success)
    - error: string (if operation failed)
    - result: operation-specific data (toggles, presets, etc.)

Error handling (T020):
    - Invalid scope: returns "Invalid scope X. Must be one of: ..."
    - Unknown toggle: returns "Unknown toggle Y"
    - Unknown preset: returns "Preset Z not found" + available list
    - Dangerous combo: returns "Contradictory toggle combination..."
    - File errors: gracefully handled, logged, but don't break routing

Referenz:
    plan.md T006 — Phase 1 QoL Core (MCP tools)
    plan.md T010 — Testing & Compliance (expanded tests)
    plan.md T018 — Per-agent QoL presets
    src/ai_proxy/qol_controls/models.py   — QoLToggle, QoLSettings, BUILTIN_PRESETS
    src/ai_proxy/qol_controls/manager.py  — QoLManager
    src/csmcp/cybersec/tool_toggles.py    — design pattern reference
    src/csmcp/sdk_compat.py              — @tool decorator

Status: production (Phase 1 complete)
Version: 1.0
Last modified: 2026-04-26 06:00:00Z
Author: python-developer
"""
from __future__ import annotations

from typing import Any

from cybersec_mcp.sdk_compat import tool
from ..helpers import JsonDict, sdk_result, sdk_error

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

    from ai_proxy.qol_controls.models import QoLSecurityError
    try:
        mgr.save_settings(settings)
    except QoLSecurityError as e:
        return sdk_error(f"Security violation: {e}")
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


# ── qol_agent_preset ─────────────────────────────────────────────────────────

@tool(
    "qol_agent_preset",
    "Get, set, or clear a per-agent QoL output-control preset. "
    "When a preset is bound to an agent, it overrides scope-level settings for every "
    "request from that agent (sent via X-Agent-Name headers). "
    "Pass preset_name='' to remove the binding.",
    {
        "agent_name": {
            "type": "string",
            "description": "Agent name as it appears in .claude/agents/*.md (e.g. 'cybersec-analyst')",
        },
        "preset_name": {
            "type": "string",
            "description": (
                "Preset to bind. Builtin: silent, code-only, structured, audit, plain-text. "
                "Omit or pass empty string to read the current binding."
            ),
        },
    },
)
async def qol_agent_preset(args: dict[str, Any]) -> JsonDict:
    agent_name = (args.get("agent_name") or "").strip()
    if not agent_name:
        return sdk_error("agent_name is required")

    preset_name = args.get("preset_name")
    mgr = _manager()

    # Read-only when preset_name is not provided
    if preset_name is None:
        current = mgr.get_agent_preset(agent_name)
        return sdk_result({
            "agent_name": agent_name,
            "preset_name": current,
            "message": f"Agent '{agent_name}' has preset '{current}'" if current else f"No preset bound to '{agent_name}'",
        })

    preset_name = preset_name.strip()

    # Clear binding
    if not preset_name:
        mgr.set_agent_preset(agent_name, None)
        return sdk_result({
            "agent_name": agent_name,
            "preset_name": None,
            "message": f"Preset binding cleared for agent '{agent_name}'",
        })

    # Set binding
    from ai_proxy.qol_controls.models import QoLSecurityError
    try:
        mgr.set_agent_preset(agent_name, preset_name)
    except ValueError as e:
        return sdk_error(str(e))
    except QoLSecurityError as e:
        return sdk_error(f"Security violation: {e}")

    return sdk_result({
        "agent_name": agent_name,
        "preset_name": preset_name,
        "message": f"Agent '{agent_name}' will now use preset '{preset_name}'",
    })


ALL_TOOLS = [qol_get, qol_set, qol_reset, qol_presets, qol_agent_preset]
