"""Findings and IOC tools — SDK in-process MCP server module."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from ..sdk_compat import tool
from ..helpers import (
    JsonDict, _get_current_scope, _coerce_limit, get_project_dir, get_session_dir,
    sdk_result, sdk_error,
)


@tool(
    "add_finding",
    "Add a new security finding to the scoped store (file + DB).",
    {
        "title": "string",
        "description": {"type": "string", "default": ""},
        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"},
        "location": {"type": "string", "default": ""},
        "status": {"type": "string", "enum": ["open", "investigating", "confirmed", "false_positive", "resolved", "accepted_risk"], "default": "open"},
        "confidence": {"type": "string", "enum": ["low", "medium", "high", "confirmed"], "default": "medium"},
        "tags": {"type": "array", "items": {"type": "string"}, "default": []},
    },
)
async def add_finding(args: dict[str, Any]) -> JsonDict:
    try:
        from hooks.database import write_scoped_entry_async
    except ImportError:
        write_scoped_entry_async = None

    title = args["title"]
    description = args.get("description", "")
    severity = args.get("severity", "medium")
    location = args.get("location", "")
    status = args.get("status", "open")
    confidence = args.get("confidence", "medium")
    tags = args.get("tags", [])

    scope = _get_current_scope()
    timestamp = datetime.now().isoformat()
    entry = (
        f"### {timestamp} — {title}\n"
        f"**Severity:** {severity.upper()}\n"
        f"**Status:** {status}\n"
        f"**Location:** {location or 'N/A'}\n\n"
        f"{description}\n\n---\n\n"
    )

    project_dir = get_project_dir(scope)
    session_dir = get_session_dir(scope)

    project_dir.mkdir(parents=True, exist_ok=True)
    if session_dir:
        session_dir.mkdir(parents=True, exist_ok=True)
        with (session_dir / f"{severity}.md").open("a", encoding="utf-8") as f:
            f.write(entry)

    with (project_dir / "findings.md").open("a", encoding="utf-8") as f:
        f.write(entry)

    data: JsonDict = {
        "title": title, "description": description, "severity": severity,
        "location": location, "status": status, "confidence": confidence,
        "tags": tags, "timestamp": timestamp,
    }
    if write_scoped_entry_async:
        await write_scoped_entry_async(
            project_name=scope["project"],
            session_id=scope["session"], value_type="finding", data=data,
        )

    return sdk_result({
        "status": "success",
        "message": f"Added {severity} finding: {title}",
        "scope": scope,
    })


@tool(
    "add_ioc",
    "Add or merge an IOC (indicator of compromise) into scoped memory and DB.",
    {
        "value": "string",
        "ioc_type": {"type": "string", "default": "unknown"},
        "confidence": {"type": "string", "enum": ["low", "medium", "high", "confirmed"], "default": "low"},
        "status": {"type": "string", "enum": ["active", "cleared", "watchlist", "expired"], "default": "active"},
        "source": {"type": "string", "default": ""},
        "context": {"type": "object", "default": {}},
        "tags": {"type": "array", "items": {"type": "string"}, "default": []},
    },
)
async def add_ioc(args: dict[str, Any]) -> JsonDict:
    value = args.get("value", "")
    if not value.strip():
        return sdk_error("IOC value is required")

    try:
        from hooks.database import write_scoped_entry_async
    except ImportError:
        write_scoped_entry_async = None

    scope = _get_current_scope()
    ioc_data: JsonDict = {
        "ioc_type": args.get("ioc_type", "unknown"),
        "value": value.strip(),
        "confidence": args.get("confidence", "low"),
        "status": args.get("status", "active"),
        "source": args.get("source", ""),
        "context": args.get("context", {}),
        "tags": args.get("tags", []),
        "timestamp": datetime.now().isoformat(),
    }
    if write_scoped_entry_async:
        await write_scoped_entry_async(
            project_name=scope["project"],
            session_id=scope["session"], value_type="ioc", data=ioc_data,
        )

    return sdk_result({"status": "success", "ioc": ioc_data, "scope": scope})


@tool(
    "query_findings",
    "Query security findings from the scoped store with optional severity/status filters.",
    {
        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"], "nullable": True},
        "status": {"type": "string", "enum": ["open", "investigating", "confirmed", "false_positive", "resolved", "accepted_risk"], "nullable": True},
        "limit": {"type": "integer", "default": 10},
    },
)
async def query_findings(args: dict[str, Any]) -> JsonDict:
    try:
        from hooks.database import query_findings_db_async, ScopeContext
    except ImportError:
        return sdk_error("hooks.database not available")

    scope = _get_current_scope()
    sc = ScopeContext(
        project_name=scope["project"],
        session_id=scope["session"],
    )
    findings = await query_findings_db_async(
        scope=sc,
        severity=args.get("severity"),
        status=args.get("status"),
        limit=_coerce_limit(args.get("limit", 10), 10),
    )
    return sdk_result({"status": "success", "findings": findings, "count": len(findings)})


@tool(
    "update_risk_register",
    "Update a risk register entry with impact, likelihood, and mitigation details.",
    {
        "risk_id": "string",
        "impact": {"type": "string", "nullable": True},
        "likelihood": {"type": "string", "nullable": True},
        "mitigation": {"type": "string", "nullable": True},
    },
)
async def update_risk_register(args: dict[str, Any]) -> JsonDict:
    try:
        from hooks.database import write_scoped_entry_async
    except ImportError:
        write_scoped_entry_async = None

    scope = _get_current_scope()
    risk_data: JsonDict = {"risk_id": args["risk_id"]}
    for field in ("impact", "likelihood", "mitigation"):
        if args.get(field) is not None:
            risk_data[field] = args[field]

    if write_scoped_entry_async:
        await write_scoped_entry_async(
            project_name=scope["project"],
            session_id=scope["session"], value_type="risk", data=risk_data,
        )

    return sdk_result({"status": "success", "message": f"Updated risk {args['risk_id']}", "data": risk_data})


ALL_TOOLS = [add_finding, add_ioc, query_findings, update_risk_register]
