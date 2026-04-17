"""Scope layer share/read tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import (
    JsonDict, _get_current_scope, _normalize_target_scopes, _normalize_scope_level,
    _coerce_limit, sdk_result, sdk_error,
)


@tool(
    "share_to_layers",
    "Share a value to one or more scopes (workspace / project / session).",
    {
        "value_type": "string",
        "data": "object",
        "target_scopes": {"type": "array", "items": {"type": "string"}, "nullable": True},
    },
)
async def share_to_layers(args: dict[str, Any]) -> JsonDict:
    try:
        from hooks.database import write_scoped_entry_async
    except ImportError:
        return sdk_error("hooks.database not available")

    scope = _get_current_scope()
    value_type = args["value_type"]
    data = args["data"]
    scopes = _normalize_target_scopes(args.get("target_scopes"))
    results: dict[str, JsonDict] = {}

    if "workspace" in scopes:
        try:
            results["workspace"] = await write_scoped_entry_async(
                workspace_name=scope["workspace"], project_name=None, session_id=None,
                value_type=value_type, data=data,
            )
        except Exception as e:
            results["workspace"] = {"status": "error", "message": str(e)}

    if "project" in scopes:
        if scope["project"]:
            try:
                results["project"] = await write_scoped_entry_async(
                    workspace_name=scope["workspace"], project_name=scope["project"],
                    session_id=None, value_type=value_type, data=data,
                )
            except Exception as e:
                results["project"] = {"status": "error", "message": str(e)}
        else:
            results["project"] = {"status": "skipped", "message": "Project scope not available"}

    if "session" in scopes:
        if scope["session"]:
            try:
                results["session"] = await write_scoped_entry_async(
                    workspace_name=scope["workspace"], project_name=scope["project"],
                    session_id=scope["session"], value_type=value_type, data=data,
                )
            except Exception as e:
                results["session"] = {"status": "error", "message": str(e)}
        else:
            results["session"] = {"status": "skipped", "message": "Session scope not available"}

    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    return sdk_result({
        "status": "success",
        "message": f"Shared {value_type} to {success_count} scopes",
        "details": results,
        "scope": scope,
    })


@tool(
    "get_layer_value",
    "Read values from a scope layer (workspace / project / session).",
    {
        "value_type": "string",
        "scope": {"type": "string", "enum": ["workspace", "project", "session"], "default": "project"},
        "layer": {"type": "string", "nullable": True},
        "limit": {"type": "integer", "default": 100},
    },
)
async def get_layer_value(args: dict[str, Any]) -> JsonDict:
    try:
        from hooks.database import get_scoped_entries_async, ScopeContext
    except ImportError:
        return sdk_error("hooks.database not available")

    current_scope = _get_current_scope()
    scope_level = _normalize_scope_level(args.get("scope", "project"), "project")

    if args.get("layer") is not None:
        layer_map = {"system": "workspace", "project": "project", "session": "session"}
        scope_level = layer_map.get(args["layer"].strip().lower(), "project")

    sc = ScopeContext(
        workspace_name=current_scope["workspace"],
        project_name=current_scope["project"] if scope_level in ("project", "session") else None,
        session_id=current_scope["session"] if scope_level == "session" else None,
    )
    data = await get_scoped_entries_async(
        workspace_name=sc.workspace_name, project_name=sc.project_name,
        session_id=sc.session_id, value_type=args["value_type"],
        limit=_coerce_limit(args.get("limit", 100), 100),
    )
    return sdk_result({
        "status": "success", "scope_level": scope_level, "scope": current_scope,
        "data": data, "count": len(data),
    })


ALL_TOOLS = [share_to_layers, get_layer_value]
