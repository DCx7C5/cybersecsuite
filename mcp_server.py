#!/usr/bin/env python3
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Final, Literal, TypedDict

from fastmcp import FastMCP

from db.bootstrap import (
    get_database_health_async,
    init_tortoise_async,
    bootstrap_intelligence_async as bootstrap_intelligence_db_async,
)
from hooks.database import (
    ScopeContext,
    get_recent_entries_async,
    get_scoped_entries_async,
    query_findings_db_async,
    write_scoped_entry_async,
)
from hooks.uvloop_integration import get_event_loop_info
from hooks.exact_match_cache import (
    cache_analytics_async,
    cache_get_async,
    cache_invalidate_async,
    cache_put_async,
    compute_cache_key,
)

JsonDict = dict[str, Any]


class ScopeState(TypedDict):
    workspace: str
    project: str | None
    session: str | None


FINDING_SEVERITIES: Final[tuple[str, ...]] = ("low", "medium", "high", "critical")
FINDING_STATUSES: Final[tuple[str, ...]] = (
    "open",
    "investigating",
    "confirmed",
    "false_positive",
    "resolved",
    "accepted_risk",
)
IOC_STATUSES: Final[tuple[str, ...]] = ("active", "cleared", "watchlist", "expired")
CONFIDENCE_LEVELS: Final[tuple[str, ...]] = ("low", "medium", "high", "confirmed")
SCOPE_LEVELS: Final[tuple[str, ...]] = ("workspace", "project", "session")

# ====================== DYNAMIC CONFIGURATION ======================
def _get_base_dir() -> Path:
    base_dir = os.environ.get("CYBERSEC_BASE_DIR") or os.environ.get("MALWAREHUNTER_BASE_DIR")
    if base_dir:
        return Path(base_dir).expanduser().resolve()
    plugin_data_dir = os.environ.get("PLUGIN_DATA_DIR") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if plugin_data_dir:
        return (Path(plugin_data_dir).expanduser().resolve() / "cybersec")
    return Path(__file__).resolve().parent / "data"


def _normalize_scope_value(value: str | None, fallback: str | None = None) -> str | None:
    if value is None:
        return fallback
    normalized = value.strip()
    return normalized or fallback


def _get_current_scope() -> ScopeState:
    workspace = _normalize_scope_value(os.environ.get("CYBERSEC_WORKSPACE"), "default") or "default"
    project = _normalize_scope_value(os.environ.get("CYBERSEC_PROJECT"), "default")
    session = _normalize_scope_value(os.environ.get("CYBERSEC_SESSION_ID"))
    return {"workspace": workspace, "project": project, "session": session}


_BASE_DIR = _get_base_dir()
_WORKSPACE_DIR = _BASE_DIR / "workspaces"
_PROJECT_DIR = Path(os.environ.get("CYBERSEC_PROJECT_DIR", str(Path.cwd()))).expanduser().resolve()
_SESSION_BASE = _BASE_DIR / "sessions"


def _initialize_scope() -> None:
    _WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    _PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    _SESSION_BASE.mkdir(parents=True, exist_ok=True)


def _build_scope_context(scope: ScopeState) -> ScopeContext:
    return ScopeContext(
        workspace_name=scope["workspace"],
        project_name=scope["project"],
        session_id=scope["session"],
    )


def _normalize_choice(value: Any, allowed: tuple[str, ...], default: str) -> str:
    if value is None:
        return default
    normalized = str(value).strip().lower()
    return normalized if normalized in allowed else default


def _coerce_limit(value: Any, default: int, maximum: int = 500) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(limit, maximum))


def _normalize_target_scopes(value: Any) -> list[str]:
    if value is None:
        return list(SCOPE_LEVELS)
    if not isinstance(value, list):
        raise ValueError("target_scopes must be an array of scope names")
    normalized: list[str] = []
    for item in value:
        scope_name = str(item).strip().lower()
        if scope_name not in SCOPE_LEVELS:
            raise ValueError(f"Unsupported scope '{item}'. Allowed scopes: {', '.join(SCOPE_LEVELS)}")
        if scope_name not in normalized:
            normalized.append(scope_name)
    return normalized or list(SCOPE_LEVELS)


def _normalize_scope_level(value: Any, default: str = "project") -> str:
    normalized = str(value).strip().lower() if value is not None else default
    if normalized not in SCOPE_LEVELS:
        raise ValueError(f"Unsupported scope '{normalized}'. Allowed scopes: {', '.join(SCOPE_LEVELS)}")
    return normalized


def get_workspace_dir(scope: ScopeState | None = None) -> Path:
    scope = scope or _get_current_scope()
    return _WORKSPACE_DIR / scope["workspace"]


def get_project_dir(scope: ScopeState | None = None) -> Path:
    scope = scope or _get_current_scope()
    workspace_dir = get_workspace_dir(scope)
    return workspace_dir / "projects" / scope["project"] if scope["project"] else _PROJECT_DIR


def get_session_dir(scope: ScopeState | None = None) -> Path | None:
    scope = scope or _get_current_scope()
    if scope["session"]:
        project_dir = get_project_dir(scope)
        return project_dir / "sessions" / scope["session"]
    return None


# ====================== FastMCP SERVER ======================
mcp = FastMCP("cybersec")
_initialize_scope()


# ====================== TOOL IMPLEMENTATIONS ======================

@mcp.tool(name="cybersec.add_finding")
async def add_finding(
    title: str,
    description: str = "",
    severity: Literal["low", "medium", "high", "critical"] = "medium",
    location: str = "",
    status: Literal[
        "open", "investigating", "confirmed", "false_positive", "resolved", "accepted_risk"
    ] = "open",
    confidence: Literal["low", "medium", "high", "confirmed"] = "medium",
    tags: list[str] | None = None,
) -> JsonDict:
    """Add a new security finding to the scoped store."""
    scope = _get_current_scope()
    timestamp = datetime.now().isoformat()
    entry = (
        f"### {timestamp} — {title}\n"
        f"**Severity:** {severity.upper()}\n"
        f"**Status:** {status}\n"
        f"**Location:** {location or 'N/A'}\n\n"
        f"{description}\n\n---\n\n"
    )

    workspace_dir = get_workspace_dir(scope)
    project_dir = get_project_dir(scope)
    session_dir = get_session_dir(scope)

    workspace_dir.mkdir(parents=True, exist_ok=True)
    project_dir.mkdir(parents=True, exist_ok=True)
    if session_dir:
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / f"{severity}.md").open("a", encoding="utf-8").write(entry)

    with (project_dir / "findings.md").open("a", encoding="utf-8") as f:
        f.write(entry)

    if workspace_dir != project_dir:
        with (workspace_dir / "findings.md").open("a", encoding="utf-8") as f:
            f.write(entry)

    data: JsonDict = {
        "title": title,
        "description": description,
        "severity": severity,
        "location": location,
        "status": status,
        "confidence": confidence,
        "tags": tags or [],
        "timestamp": timestamp,
    }
    await write_scoped_entry_async(
        workspace_name=scope["workspace"],
        project_name=scope["project"],
        session_id=scope["session"],
        value_type="finding",
        data=data,
    )

    return {
        "status": "success",
        "message": f"Added {severity} finding to scope {scope['workspace']}/{scope['project']}/{scope['session'] or 'none'}",
        "scope": scope,
        "loop_info": get_event_loop_info(),
    }


@mcp.tool(name="cybersec.add_ioc")
async def add_ioc(
    value: str,
    ioc_type: str = "unknown",
    confidence: Literal["low", "medium", "high", "confirmed"] = "low",
    status: Literal["active", "cleared", "watchlist", "expired"] = "active",
    source: str = "",
    context: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> JsonDict:
    """Add or merge an IOC into scoped memory."""
    if not value.strip():
        raise ValueError("IOC value is required")
    scope = _get_current_scope()
    ioc_data: JsonDict = {
        "ioc_type": ioc_type.strip() or "unknown",
        "value": value.strip(),
        "confidence": confidence,
        "status": status,
        "source": source,
        "context": context or {},
        "tags": tags or [],
        "timestamp": datetime.now().isoformat(),
    }
    sync_result = await write_scoped_entry_async(
        workspace_name=scope["workspace"],
        project_name=scope["project"],
        session_id=scope["session"],
        value_type="ioc",
        data=ioc_data,
    )
    return {
        "status": "success",
        "message": f"Stored IOC {value} in scope {scope['workspace']}/{scope['project']}/{scope['session'] or 'none'}",
        "ioc": ioc_data,
        "sync": sync_result,
        "scope": scope,
        "loop_info": get_event_loop_info(),
    }


@mcp.tool(name="cybersec.query_findings")
async def query_findings(
    severity: Literal["low", "medium", "high", "critical"] | None = None,
    status: Literal[
        "open", "investigating", "confirmed", "false_positive", "resolved", "accepted_risk"
    ] | None = None,
    limit: int = 10,
) -> JsonDict:
    """Query security findings from the scoped store."""
    scope = _get_current_scope()
    findings = await query_findings_db_async(
        scope=_build_scope_context(scope),
        severity=severity,
        status=status,
        limit=_coerce_limit(limit, 10),
    )
    return {
        "status": "success",
        "findings": findings,
        "count": len(findings),
        "scope": scope,
        "async": True,
    }


@mcp.tool(name="cybersec.update_risk_register")
async def update_risk_register(
    risk_id: str,
    impact: str | None = None,
    likelihood: str | None = None,
    mitigation: str | None = None,
) -> JsonDict:
    """Update a risk register entry."""
    scope = _get_current_scope()
    risk_data: JsonDict = {"risk_id": risk_id}
    if impact is not None:
        risk_data["impact"] = impact
    if likelihood is not None:
        risk_data["likelihood"] = likelihood
    if mitigation is not None:
        risk_data["mitigation"] = mitigation

    sync_result = await write_scoped_entry_async(
        workspace_name=scope["workspace"],
        project_name=scope["project"],
        session_id=scope["session"],
        value_type="risk",
        data=risk_data,
    )
    return {
        "status": "success",
        "message": f"Updated risk {risk_id}",
        "data": risk_data,
        "sync": sync_result,
        "scope": scope,
        "async": True,
        "loop_info": get_event_loop_info(),
    }


@mcp.tool(name="cybersec.get_project_memory")
async def get_project_memory(query: str = "") -> JsonDict:
    """Return project memory: findings, recent entries and IOCs from the current scope."""
    scope = _get_current_scope()
    session_dir = get_session_dir(scope)
    findings_file = get_project_dir(scope) / "findings.md"
    memory_data: JsonDict = {
        "findings": "",
        "scope": scope,
        "workspace_dir": str(get_workspace_dir(scope)),
        "project_dir": str(get_project_dir(scope)),
        "session_dir": str(session_dir) if session_dir else None,
    }
    if findings_file.exists():
        memory_data["findings"] = findings_file.read_text(encoding="utf-8")

    scope_context = _build_scope_context(scope)
    memory_data["recent_entries"] = await get_recent_entries_async(scope_context, limit=20)
    memory_data["recent_iocs"] = await get_scoped_entries_async(
        workspace_name=scope["workspace"],
        project_name=scope["project"],
        session_id=scope["session"],
        value_type="ioc",
        limit=10,
    )
    return {
        "status": "success",
        "memory": memory_data,
        "query": query,
        "scope": scope,
        "async": True,
        "loop_info": get_event_loop_info(),
    }


@mcp.tool(name="cybersec.db_healthcheck")
async def db_healthcheck(
    check_connection: bool = True,
    create_db: bool = False,
    bootstrap_intel: bool = False,
    include_counts: bool = True,
) -> JsonDict:
    """Check PostgreSQL/Tortoise health and optional table/intelligence counts."""
    health = await get_database_health_async(
        create_db=create_db,
        bootstrap_intel=bootstrap_intel,
        include_counts=include_counts,
        check_connection=check_connection,
    )
    health["loop_info"] = get_event_loop_info()
    return health


@mcp.tool(name="cybersec.bootstrap_intelligence")
async def bootstrap_intelligence(
    force: bool = False,
    include_feeds: bool = True,
    create_db: bool = True,
) -> JsonDict:
    """Bootstrap NVD/CVE, CWE, CAPEC, MITRE families and shared feeds into PostgreSQL."""
    await init_tortoise_async(create_db=create_db, bootstrap_intel=False)
    summary = await bootstrap_intelligence_db_async(force=force, include_feeds=include_feeds)
    health = await get_database_health_async(
        create_db=False,
        bootstrap_intel=False,
        include_counts=True,
        check_connection=True,
    )
    return {
        "status": "success",
        "bootstrap": summary,
        "health": health,
        "loop_info": get_event_loop_info(),
    }


@mcp.tool(name="cybersec.suggest_mitre")
def suggest_mitre(description: str, category: str = "") -> JsonDict:
    """Suggest MITRE ATT&CK techniques based on a description of observed behaviour."""
    mitre_suggestions: list[str] = []
    matched_keywords: list[str] = []
    seen: set[str] = set()

    keywords_to_mitre: dict[str, list[str]] = {
        "screenshot": ["T1113 - Screen Capture"],
        "keylog": ["T1056.001 - Keylogging"],
        "browser": ["T1555.003 - Web Browsers", "T1539 - Steal Web Session Cookie"],
        "cookie": ["T1539 - Steal Web Session Cookie"],
        "arp": ["T1557.002 - ARP Cache Poisoning"],
        "network": ["T1040 - Network Sniffing", "T1557 - Man-in-the-Middle"],
        "persistence": ["T1547 - Boot or Logon Autostart Execution"],
        "log": ["T1070.002 - Clear Windows Event Logs", "T1562.002 - Disable Windows Event Logging"],
        "injection": ["T1055 - Process Injection"],
        "c2": ["T1071 - Application Layer Protocol", "T1573 - Encrypted Channel"],
        "scheduled task": ["T1053.005 - Scheduled Task", "T1053 - Scheduled Task/Job"],
        "download": ["T1105 - Ingress Tool Transfer", "T1071.001 - Web Protocols"],
        "payload": ["T1105 - Ingress Tool Transfer", "T1204 - User Execution"],
        "task": ["T1053.005 - Scheduled Task", "T1053 - Scheduled Task/Job"],
        "cron": ["T1053.003 - Cron", "T1053 - Scheduled Task/Job"],
    }

    desc_lower = description.lower()
    for keyword, techniques in keywords_to_mitre.items():
        if keyword in desc_lower:
            matched_keywords.append(keyword)
            for technique in techniques:
                if technique not in seen:
                    seen.add(technique)
                    mitre_suggestions.append(technique)

    return {
        "status": "success",
        "description": description,
        "suggested_techniques": mitre_suggestions,
        "matched_keywords": matched_keywords,
        "category": category,
    }


@mcp.tool(name="cybersec.share_to_layers")
async def share_to_layers(
    value_type: str,
    data: dict[str, Any],
    target_scopes: list[str] | None = None,
) -> JsonDict:
    """Share a value to one or more scopes (workspace / project / session)."""
    scope = _get_current_scope()
    scopes = _normalize_target_scopes(target_scopes)
    results: dict[str, JsonDict] = {}

    if "workspace" in scopes:
        try:
            results["workspace"] = await write_scoped_entry_async(
                workspace_name=scope["workspace"],
                project_name=None,
                session_id=None,
                value_type=value_type,
                data=data,
            )
        except Exception as e:
            results["workspace"] = {"status": "error", "message": str(e)}

    if "project" in scopes:
        if scope["project"]:
            try:
                results["project"] = await write_scoped_entry_async(
                    workspace_name=scope["workspace"],
                    project_name=scope["project"],
                    session_id=None,
                    value_type=value_type,
                    data=data,
                )
            except Exception as e:
                results["project"] = {"status": "error", "message": str(e)}
        else:
            results["project"] = {"status": "skipped", "message": "Project scope not available"}

    if "session" in scopes:
        if scope["session"]:
            try:
                results["session"] = await write_scoped_entry_async(
                    workspace_name=scope["workspace"],
                    project_name=scope["project"],
                    session_id=scope["session"],
                    value_type=value_type,
                    data=data,
                )
            except Exception as e:
                results["session"] = {"status": "error", "message": str(e)}
        else:
            results["session"] = {"status": "skipped", "message": "Session scope not available"}

    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    return {
        "status": "success",
        "message": f"Shared {value_type} to {success_count} scopes",
        "details": results,
        "scope": scope,
        "loop_info": get_event_loop_info(),
    }


@mcp.tool(name="cybersec.get_layer_value")
async def get_layer_value(
    value_type: str,
    scope: Literal["workspace", "project", "session"] = "project",
    layer: str | None = None,
    limit: int = 100,
) -> JsonDict:
    """Read values from a scope layer (workspace / project / session)."""
    current_scope = _get_current_scope()
    scope_level = _normalize_scope_level(scope, "project")

    # Legacy "layer" param → scope mapping
    if layer is not None:
        layer_mapping = {"system": "workspace", "project": "project", "session": "session"}
        scope_level = layer_mapping.get(layer.strip().lower(), "project")

    scope_context = ScopeContext(
        workspace_name=current_scope["workspace"],
        project_name=current_scope["project"] if scope_level in ("project", "session") else None,
        session_id=current_scope["session"] if scope_level == "session" else None,
    )

    data = await get_scoped_entries_async(
        workspace_name=scope_context.workspace_name,
        project_name=scope_context.project_name,
        session_id=scope_context.session_id,
        value_type=value_type,
        limit=_coerce_limit(limit, 100),
    )

    return {
        "status": "success",
        "scope_level": scope_level,
        "scope": current_scope,
        "data": data,
        "count": len(data),
        "async": True,
        "loop_info": get_event_loop_info(),
    }


# ====================== EXACT-MATCH CONTEXT CACHING ======================

@mcp.tool(name="cybersec.cache_lookup")
async def cache_lookup(
    tool_name: str,
    params: dict[str, Any],
) -> JsonDict:
    """Exact-match cache lookup for a tool call.

    Computes a deterministic SHA-256 key from *tool_name* + *params*, then
    returns the cached result (hit) or ``{"hit": false}`` (miss) so the
    caller can decide whether to execute the real tool.

    Step-by-step (exact-match-context-caching skill):
    1. Canonical JSON of {tool_name, params} → SHA-256 → cache key
    2. Query Redis (or in-memory fallback)
    3. Return cached payload on hit; miss indicator on miss
    """
    key_input = {"tool": tool_name, "params": params}
    key = compute_cache_key(key_input)
    entry = await cache_get_async(key)
    if entry is not None:
        return {
            "hit": True,
            "key": key,
            "result": entry.get("result"),
            "tokens_saved": entry.get("tokens_saved", 0),
            "cached_at": entry.get("timestamp"),
            "loop_info": get_event_loop_info(),
        }
    return {
        "hit": False,
        "key": key,
        "loop_info": get_event_loop_info(),
    }


@mcp.tool(name="cybersec.cache_store")
async def cache_store(
    tool_name: str,
    params: dict[str, Any],
    result: str,
    tokens_saved: int = 0,
    ttl_seconds: int | None = None,
) -> JsonDict:
    """Store a tool result in the exact-match cache.

    Computes the same deterministic key as ``cybersec.cache_lookup`` and
    writes *result* with TTL enforcement. Use after executing a cacheable
    tool call so subsequent identical calls are served from cache.

    Args:
        tool_name:    Name of the MCP tool whose output is being cached.
        params:       Exact params dict used for the call (determines key).
        result:       Serialised result to cache (JSON string recommended).
        tokens_saved: Estimated token savings for analytics tracking.
        ttl_seconds:  Override TTL; defaults to CACHE_TTL_SECONDS (24 h).
    """
    key_input = {"tool": tool_name, "params": params}
    key = compute_cache_key(key_input)
    confirmation = await cache_put_async(key, result, tokens_saved, ttl_seconds)
    return {
        "status": "success",
        "key": key,
        "message": confirmation,
        "loop_info": get_event_loop_info(),
    }


@mcp.tool(name="cybersec.cache_analytics")
async def cache_analytics_tool() -> JsonDict:
    """Return live cache statistics: entry count, total token savings, backend.

    Covers all ``cybersec:`` prefixed keys in Redis (or the in-memory store
    when Redis is unavailable).
    """
    stats = await cache_analytics_async()
    return {
        "status": "success",
        "analytics": stats,
        "loop_info": get_event_loop_info(),
    }


@mcp.tool(name="cybersec.cache_invalidate")
async def cache_invalidate_tool(
    tool_name: str,
    params: dict[str, Any],
) -> JsonDict:
    """Invalidate a specific cache entry by recomputing its key.

    Uses the same deterministic hash as ``cybersec.cache_lookup`` /
    ``cybersec.cache_store``. Useful after the underlying data changes
    and a stale cached result must be evicted immediately (before TTL).
    """
    key_input = {"tool": tool_name, "params": params}
    key = compute_cache_key(key_input)
    message = await cache_invalidate_async(key)
    return {
        "status": "success",
        "key": key,
        "message": message,
        "loop_info": get_event_loop_info(),
    }


if __name__ == "__main__":
    mcp.run()
