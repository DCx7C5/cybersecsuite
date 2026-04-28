"""
Tool toggle system — per-scope enable/disable with single-scope exclusivity.

A tool can be toggled on or off at any scope level (project, session).
The exclusivity rule: a tool may only be *enabled* at ONE scope at a time.
Enabling at scope X automatically disables it at every other scope.

Storage layout (all JSON, no DB):
  {base_dir}/tool_toggles.json            — global registry: tool → active scope
  {project_dir}/tool_toggles.json         — project-scope toggle states
  {session_dir}/tool_toggles.json         — session-scope toggle states (if session active)

Toggle state file format:
  {"toggles": {"tool_name": {"enabled": bool, "updated_at": "ISO8601"}}}

Registry format:
  {"active": {"tool_name": "project"|"session"|null}}
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ..sdk_compat import tool
from ..helpers import (
    JsonDict,
    _get_current_scope,
    _get_base_dir,
    get_project_dir,
    get_session_dir,
    sdk_result,
    sdk_error,
)

_ALL_SCOPE_LEVELS = ("global", "project", "session")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _registry_path() -> Path:
    return _get_base_dir() / "tool_toggles.json"


def _scope_file_path(scope_level: str) -> Path | None:
    """Return the path to the toggle file for the given scope level."""
    if scope_level == "global":
        return _get_base_dir() / "tool_toggles_global.json"
    if scope_level == "project":
        return get_project_dir() / "tool_toggles.json"
    if scope_level == "session":
        session_dir = get_session_dir()
        if session_dir is None:
            return None
        return session_dir / "tool_toggles.json"
    return None


def _load_json(path: Path) -> dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ── Registry helpers (tracks which scope holds the active toggle per tool) ────

def _load_registry() -> dict[str, Any]:
    data = _load_json(_registry_path())
    data.setdefault("active", {})
    return data


def _save_registry(reg: dict[str, Any]) -> None:
    _save_json(_registry_path(), reg)


def _active_scope_for(tool_name: str) -> Optional[str]:
    """Return the scope that currently has this tool *enabled*, or None."""
    return _load_registry()["active"].get(tool_name)


# ── Per-scope state helpers ───────────────────────────────────────────────────

def _load_scope_toggles(scope_level: str) -> dict[str, Any]:
    path = _scope_file_path(scope_level)
    if path is None:
        return {}
    data = _load_json(path)
    data.setdefault("toggles", {})
    return data


def _save_scope_toggles(scope_level: str, data: dict[str, Any]) -> None:
    path = _scope_file_path(scope_level)
    if path is not None:
        _save_json(path, data)


def _set_tool_in_scope(scope_level: str, tool_name: str, enabled: bool) -> None:
    data = _load_scope_toggles(scope_level)
    data["toggles"][tool_name] = {"enabled": enabled, "updated_at": _now()}
    _save_scope_toggles(scope_level, data)


def _clear_tool_in_scope(scope_level: str, tool_name: str) -> None:
    """Remove a tool's toggle entry from a scope file entirely."""
    data = _load_scope_toggles(scope_level)
    data["toggles"].pop(tool_name, None)
    _save_scope_toggles(scope_level, data)


# ── Public read API (used by _get_effective_toggles below) ───────────────────

def get_effective_state(tool_name: str) -> dict[str, Any]:
    """
    Return the *effective* toggle state for a single tool.

    Resolution: session > project > global > default (enabled=True = not toggled off)
    Returns: {enabled: bool, active_scope: str|None, per_scope: {...}}
    """
    registry = _load_registry()
    active_scope = registry["active"].get(tool_name)

    per_scope: dict[str, Any] = {}
    for lvl in _ALL_SCOPE_LEVELS:
        path = _scope_file_path(lvl)
        if path is None:
            per_scope[lvl] = {"available": False}
            continue
        data = _load_scope_toggles(lvl)
        entry = data["toggles"].get(tool_name)
        per_scope[lvl] = {"available": True, "entry": entry}

    # Effective enabled state comes from the active scope
    enabled: bool = True  # default: all tools enabled unless explicitly toggled off
    if active_scope:
        scope_data = _load_scope_toggles(active_scope)
        entry = scope_data["toggles"].get(tool_name, {})
        enabled = entry.get("enabled", True)

    return {"enabled": enabled, "active_scope": active_scope, "per_scope": per_scope}


def get_all_toggles() -> dict[str, Any]:
    """
    Return all tools that have an explicit toggle state (any scope).
    Only tools that appear in at least one scope file are returned.
    """
    seen: dict[str, dict[str, Any]] = {}
    registry = _load_registry()

    for lvl in _ALL_SCOPE_LEVELS:
        path = _scope_file_path(lvl)
        if path is None:
            continue
        data = _load_scope_toggles(lvl)
        for tool_name, entry in data.get("toggles", {}).items():
            if tool_name not in seen:
                seen[tool_name] = {
                    "active_scope": registry["active"].get(tool_name),
                    "scopes": {},
                }
            seen[tool_name]["scopes"][lvl] = entry

    # Resolve effective enabled state
    for tool_name, info in seen.items():
        active = info["active_scope"]
        if active and active in info["scopes"]:
            info["enabled"] = info["scopes"][active].get("enabled", True)
        else:
            info["enabled"] = True  # no active scope = not restricted

    return seen


# ── MCP Tools ─────────────────────────────────────────────────────────────────

@tool(
    "tool_toggle_set",
    (
        "Enable or disable a named MCP tool at a specific scope level. "
        "EXCLUSIVE: enabling a tool locks it to that scope — it is automatically "
        "disabled/cleared at all other scopes. Only one scope may have a tool enabled=true "
        "at a time. Scopes: global (all projects), project, session."
    ),
    {
        "tool_name": {
            "type": "string",
            "description": "MCP tool name to toggle, e.g. 'vault_scaffold' or 'canvas_create'",
        },
        "scope": {
            "type": "string",
            "enum": list(_ALL_SCOPE_LEVELS),
            "description": "Scope at which to apply the toggle (global / project / session)",
        },
        "enabled": {
            "type": "boolean",
            "description": "True = enable the tool at this scope; False = disable it at this scope",
        },
    },
)
async def tool_toggle_set(args: dict[str, Any]) -> JsonDict:
    tool_name = (args.get("tool_name") or "").strip()
    scope_level = (args.get("scope") or "project").strip().lower()
    enabled = bool(args.get("enabled", True))

    if not tool_name:
        return sdk_error("'tool_name' is required")
    if scope_level not in _ALL_SCOPE_LEVELS:
        return sdk_error(f"'scope' must be one of: {', '.join(_ALL_SCOPE_LEVELS)}")

    # Validate session scope availability
    if scope_level == "session" and get_session_dir() is None:
        return sdk_error("Session scope unavailable — CYBERSEC_SESSION_ID not set")

    registry = _load_registry()
    current_active = registry["active"].get(tool_name)
    cleared_scopes: list[str] = []

    if enabled:
        # Exclusivity: clear this tool's enabled state from every other scope
        for other_scope in _ALL_SCOPE_LEVELS:
            if other_scope == scope_level:
                continue
            other_path = _scope_file_path(other_scope)
            if other_path is None:
                continue
            other_data = _load_scope_toggles(other_scope)
            entry = other_data["toggles"].get(tool_name, {})
            if entry.get("enabled", False):
                # Was enabled there — clear it
                _clear_tool_in_scope(other_scope, tool_name)
                cleared_scopes.append(other_scope)

        # Set enabled at requested scope
        _set_tool_in_scope(scope_level, tool_name, True)
        registry["active"][tool_name] = scope_level
    else:
        # Disable at this scope
        _set_tool_in_scope(scope_level, tool_name, False)
        # If this was the active scope, clear the registry entry
        if current_active == scope_level:
            registry["active"].pop(tool_name, None)

    _save_registry(registry)

    return sdk_result({
        "tool_name": tool_name,
        "scope": scope_level,
        "enabled": enabled,
        "active_scope": registry["active"].get(tool_name),
        "cleared_from_scopes": cleared_scopes,
        "message": (
            f"Tool '{tool_name}' {'enabled' if enabled else 'disabled'} at scope '{scope_level}'"
            + (f" (cleared from: {', '.join(cleared_scopes)})" if cleared_scopes else "")
        ),
    })


@tool(
    "tool_toggle_get",
    "Get the current toggle state for a specific tool across all scopes.",
    {
        "tool_name": {
            "type": "string",
            "description": "MCP tool name to query",
        },
    },
)
async def tool_toggle_get(args: dict[str, Any]) -> JsonDict:
    tool_name = (args.get("tool_name") or "").strip()
    if not tool_name:
        return sdk_error("'tool_name' is required")

    state = get_effective_state(tool_name)
    scope = _get_current_scope()

    return sdk_result({
        "tool_name": tool_name,
        "enabled": state["enabled"],
        "active_scope": state["active_scope"],
        "per_scope": state["per_scope"],
        "current_context": scope,
    })


@tool(
    "tool_toggle_list",
    "List all tools that have explicit toggle states, with their active scope and enabled status.",
    {
        "scope": {
            "type": "string",
            "enum": [*list(_ALL_SCOPE_LEVELS), "all"],
            "default": "all",
            "description": "Filter by scope (global/project/session/all)",
        },
        "enabled_only": {
            "type": "boolean",
            "default": False,
            "description": "Return only tools that are currently enabled",
        },
    },
)
async def tool_toggle_list(args: dict[str, Any]) -> JsonDict:
    scope_filter = (args.get("scope") or "all").strip().lower()
    enabled_only = bool(args.get("enabled_only", False))

    all_toggles = get_all_toggles()

    # Apply filters
    result: list[dict[str, Any]] = []
    for tool_name, info in sorted(all_toggles.items()):
        if scope_filter != "all" and info.get("active_scope") != scope_filter:
            continue
        if enabled_only and not info.get("enabled", True):
            continue
        result.append({
            "tool_name": tool_name,
            "enabled": info.get("enabled", True),
            "active_scope": info.get("active_scope"),
            "scopes": info.get("scopes", {}),
        })

    return sdk_result({
        "toggles": result,
        "count": len(result),
        "scope_filter": scope_filter,
        "available_scopes": _ALL_SCOPE_LEVELS,
    })


@tool(
    "tool_toggle_clear",
    "Remove all toggle state for a tool across all scopes (resets to default: enabled).",
    {
        "tool_name": {
            "type": "string",
            "description": "MCP tool name to reset",
        },
    },
)
async def tool_toggle_clear(args: dict[str, Any]) -> JsonDict:
    tool_name = (args.get("tool_name") or "").strip()
    if not tool_name:
        return sdk_error("'tool_name' is required")

    cleared: list[str] = []
    for lvl in _ALL_SCOPE_LEVELS:
        data = _load_scope_toggles(lvl)
        if tool_name in data.get("toggles", {}):
            _clear_tool_in_scope(lvl, tool_name)
            cleared.append(lvl)

    registry = _load_registry()
    registry["active"].pop(tool_name, None)
    _save_registry(registry)

    return sdk_result({
        "tool_name": tool_name,
        "cleared_from": cleared,
        "message": f"Tool '{tool_name}' reset to default (enabled) across all scopes",
    })


ALL_TOOLS = [tool_toggle_set, tool_toggle_get, tool_toggle_list, tool_toggle_clear]
