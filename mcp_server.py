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
        return Path(plugin_data_dir).expanduser().resolve() / "cybersec"
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


# ====================== AI PROXY TOOLS ======================

@mcp.tool(name="cybersec.proxy_chat")
async def proxy_chat(
    prompt: str,
    model: str = "gpt-4o-mini",
    provider: str | None = None,
    system: str | None = None,
    prefer_free: bool = False,
    max_cost_per_1k: float | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> JsonDict:
    """Route a chat completion through the AI proxy with multi-provider fallback.

    Supports 15+ providers (OpenAI, Anthropic, Gemini, DeepSeek, Groq, etc.)
    with automatic format translation, rate limiting, and cost tracking.

    Headers equivalent:
      X-Provider: force a specific provider
      X-Prefer-Free: route to free providers first
      X-Max-Cost-Per-1K: cost ceiling per 1K tokens
    """
    from ai_proxy.routing.combo import smart_route, route_request, ComboConfig, ComboTarget, Strategy

    body: JsonDict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["messages"].insert(0, {"role": "system", "content": system})
    if temperature is not None:
        body["temperature"] = temperature
    if max_tokens is not None:
        body["max_tokens"] = max_tokens

    if provider:
        combo = ComboConfig(
            id=f"mcp-{provider}",
            name=f"MCP → {provider}",
            strategy=Strategy.PRIORITY,
            targets=[ComboTarget(provider_id=provider, model_id=model)],
        )
        result = await route_request(body, combo)
    else:
        result = await smart_route(body, prefer_free=prefer_free, max_cost_per_1k=max_cost_per_1k)

    if not result.ok:
        return {"status": "error", "error": result.error, "status_code": result.status_code}

    choices = (result.body or {}).get("choices", [])
    content = choices[0].get("message", {}).get("content", "") if choices else ""
    usage = (result.body or {}).get("usage", {})

    return {
        "status": "success",
        "content": content,
        "provider": result.provider_id,
        "model": result.model_id,
        "latency_ms": round(result.latency_ms, 1),
        "usage": usage,
    }


@mcp.tool(name="cybersec.proxy_providers")
async def proxy_providers() -> JsonDict:
    """List all configured AI providers with status and rate limits."""
    from ai_proxy.providers.registry import get_all_providers
    from ai_proxy.services.rate_limiter import rate_limiter

    providers = []
    for p in get_all_providers().values():
        has_key = p.get_api_key() is not None
        providers.append({
            "id": p.id,
            "name": p.name,
            "format": p.api_format.value,
            "is_free": p.is_free,
            "has_key": has_key,
            "models": [m.id for m in p.models],
            "rate_limit": rate_limiter.get_status(p.id),
        })
    return {"status": "success", "providers": providers, "count": len(providers)}


@mcp.tool(name="cybersec.proxy_models")
async def proxy_models(provider: str | None = None) -> JsonDict:
    """List all available models across providers."""
    from ai_proxy.providers.registry import list_all_models

    models = list_all_models()
    if provider:
        models = [m for m in models if m["owned_by"] == provider]
    return {"status": "success", "models": models, "count": len(models)}


@mcp.tool(name="cybersec.proxy_usage")
async def proxy_usage() -> JsonDict:
    """Return AI proxy usage summary: tokens, costs, requests by provider."""
    from ai_proxy.services.usage_tracker import usage_tracker

    return {
        "status": "success",
        "summary": usage_tracker.get_summary(),
        "recent": usage_tracker.get_recent(limit=10),
    }


@mcp.tool(name="cybersec.proxy_cost")
async def proxy_cost() -> JsonDict:
    """Return detailed cost breakdown by provider."""
    from ai_proxy.services.usage_tracker import usage_tracker

    summary = usage_tracker.get_summary()
    return {
        "status": "success",
        "total_cost_usd": summary["total_cost_usd"],
        "total_tokens": summary["total_tokens"],
        "by_provider": summary["by_provider"],
    }


# ====================== ROUTING INTELLIGENCE TOOLS (OmniRoute-style) ======================

@mcp.tool(name="cybersec.simulate_route")
async def simulate_route(
    model: str = "gpt-4o-mini",
    prefer_free: bool = False,
    max_cost_per_1k: float | None = None,
) -> JsonDict:
    """Dry-run route simulation — shows which provider/model would be selected without executing.

    Mirrors OmniRoute's omniroute_simulate_route tool. Returns the routing
    decision path: tier classification, strategy, target ordering, circuit
    breaker state, and estimated cost.
    """
    from ai_proxy.providers.registry import get_all_providers, get_free_providers
    from ai_proxy.routing.combo import (
        get_circuit_breaker_status,
        get_usage_counts,
        budget_guard,
    )

    all_providers = get_all_providers()
    free = get_free_providers()
    usage = get_usage_counts()
    cb_status = get_circuit_breaker_status()
    open_circuits = {cb["target"] for cb in cb_status if cb["state"] == "open"}

    candidates = []
    for p in all_providers.values():
        if not p.is_available:
            continue
        for m in p.models:
            if m.deprecated:
                continue
            if model and model != m.id:
                continue
            is_blocked = f"{p.id}:{m.id}" in open_circuits
            candidates.append({
                "provider": p.id,
                "model": m.id,
                "is_free": p.is_free,
                "cost_input": m.cost.input,
                "cost_output": m.cost.output,
                "context_window": m.context_window,
                "circuit_open": is_blocked,
                "usage_count": usage.get(p.id, 0),
            })

    if prefer_free:
        candidates.sort(key=lambda c: (not c["is_free"], c["cost_input"]))
    elif max_cost_per_1k is not None:
        candidates = [c for c in candidates if c["cost_input"] <= max_cost_per_1k * 1000]
        candidates.sort(key=lambda c: c["cost_input"])
    else:
        candidates.sort(key=lambda c: c["cost_input"])

    selected = next((c for c in candidates if not c["circuit_open"]), None)

    return {
        "status": "success",
        "selected": selected,
        "candidates_total": len(candidates),
        "candidates_available": sum(1 for c in candidates if not c["circuit_open"]),
        "open_circuits": len(open_circuits),
        "budget": budget_guard.get_all(),
    }


@mcp.tool(name="cybersec.set_budget_guard")
async def set_budget_guard(
    key: str,
    budget_usd: float,
) -> JsonDict:
    """Set a spending budget guard for a combo or tier.

    Mirrors OmniRoute's omniroute_set_budget_guard. When spending exceeds
    the budget, routing will skip the guarded key.

    Args:
        key: Combo ID or tier name to guard (e.g., "premium", "combo-1")
        budget_usd: Maximum USD spending allowed
    """
    from ai_proxy.routing.combo import budget_guard

    current = budget_guard.get_spent(key)
    return {
        "status": "success",
        "key": key,
        "budget_usd": budget_usd,
        "current_spent": current,
        "remaining": max(0.0, budget_usd - current),
        "message": f"Budget guard set: ${budget_usd:.4f} for '{key}' (${current:.4f} spent)",
    }


@mcp.tool(name="cybersec.get_circuit_breakers")
async def get_circuit_breakers_tool() -> JsonDict:
    """Return circuit breaker status for all routing targets.

    Mirrors OmniRoute's circuit breaker monitoring. Shows which
    provider:model combinations are open (failing) or closed (healthy).
    """
    from ai_proxy.routing.combo import get_circuit_breaker_status

    cb_status = get_circuit_breaker_status()
    open_count = sum(1 for cb in cb_status if cb["state"] == "open")
    return {
        "status": "success",
        "circuit_breakers": cb_status,
        "total": len(cb_status),
        "open": open_count,
        "closed": len(cb_status) - open_count,
    }


@mcp.tool(name="cybersec.explain_route")
async def explain_route(
    model: str = "gpt-4o-mini",
    provider: str | None = None,
) -> JsonDict:
    """Explain why a specific provider/model would be chosen for a request.

    Mirrors OmniRoute's omniroute_explain_route. Returns a step-by-step
    explanation of the routing decision.
    """
    from ai_proxy.providers.registry import get_all_providers
    from ai_proxy.routing.combo import (
        get_circuit_breaker_status,
        get_usage_counts,
        budget_guard,
    )
    from ai_proxy.services.rate_limiter import rate_limiter

    steps: list[str] = []
    all_p = get_all_providers()
    usage = get_usage_counts()
    cb_status = get_circuit_breaker_status()
    open_targets = {cb["target"] for cb in cb_status if cb["state"] == "open"}

    # Step 1: Find matching providers
    matching = []
    for p in all_p.values():
        for m in p.models:
            if m.id == model or (not model):
                matching.append((p, m))

    steps.append(f"1. Found {len(matching)} provider(s) offering model '{model}'")

    if provider:
        matching = [(p, m) for p, m in matching if p.id == provider]
        steps.append(f"2. Filtered to provider '{provider}': {len(matching)} match(es)")

    # Step 2: Check availability
    available = [(p, m) for p, m in matching if p.is_available]
    unavailable = len(matching) - len(available)
    if unavailable:
        steps.append(f"3. {unavailable} provider(s) unavailable (no credentials)")

    # Step 3: Check circuit breakers
    cb_blocked = [(p, m) for p, m in available if f"{p.id}:{m.id}" in open_targets]
    if cb_blocked:
        steps.append(f"4. {len(cb_blocked)} target(s) blocked by circuit breaker")
        available = [(p, m) for p, m in available if f"{p.id}:{m.id}" not in open_targets]

    # Step 4: Rate limits
    rl_info = []
    for p, m in available:
        rl = rate_limiter.get_status(p.id)
        if rl:
            rl_info.append(f"   {p.id}: {rl}")
    if rl_info:
        steps.append("5. Rate limit status:\n" + "\n".join(rl_info))

    # Step 5: Cost ranking
    available.sort(key=lambda pm: pm[1].cost.input)
    if available:
        p, m = available[0]
        steps.append(
            f"6. Selected: {p.id}/{m.id} "
            f"(${m.cost.input}/M in, ${m.cost.output}/M out, "
            f"{usage.get(p.id, 0)} prior requests)"
        )

    return {
        "status": "success",
        "model": model,
        "provider": provider,
        "steps": steps,
        "selected": {"provider": available[0][0].id, "model": available[0][1].id} if available else None,
        "budget": budget_guard.get_all(),
    }


@mcp.tool(name="cybersec.routing_strategies")
async def routing_strategies() -> JsonDict:
    """List all available routing strategies with descriptions.

    Mirrors OmniRoute's 13 combo strategies.
    """
    from ai_proxy.routing.combo import Strategy

    strategies = [
        {"id": s.value, "name": s.name.replace("_", " ").title()}
        for s in Strategy
    ]
    return {"status": "success", "strategies": strategies, "count": len(strategies)}


@mcp.tool(name="cybersec.session_snapshot")
async def session_snapshot() -> JsonDict:
    """Return a full session state snapshot.

    Mirrors OmniRoute's omniroute_get_session_snapshot. Includes scope,
    usage, budget, circuit breakers, and provider status.
    """
    from ai_proxy.providers.registry import get_enabled_providers, get_free_providers
    from ai_proxy.routing.combo import (
        get_circuit_breaker_status,
        get_usage_counts,
        budget_guard,
        Strategy,
    )
    from ai_proxy.services.usage_tracker import usage_tracker

    scope = _get_current_scope()
    cb_status = get_circuit_breaker_status()
    usage = get_usage_counts()
    summary = usage_tracker.get_summary()
    enabled = get_enabled_providers()
    free = get_free_providers()

    return {
        "status": "success",
        "scope": scope,
        "providers": {
            "enabled": len(enabled),
            "free": len(free),
        },
        "usage": summary,
        "usage_counts": usage,
        "budget": budget_guard.get_all(),
        "circuit_breakers": {
            "total": len(cb_status),
            "open": sum(1 for cb in cb_status if cb["state"] == "open"),
        },
        "strategies_available": [s.value for s in Strategy],
        "loop_info": get_event_loop_info(),
    }


@mcp.tool(name="cybersec.agent_registry")
async def agent_registry_tool() -> JsonDict:
    """List all registered A2A agents with skills and metadata.

    Uses the AgentRegistry to discover all local (.claude/agents/*.md)
    and remote agents dynamically.
    """
    try:
        from a2a.registry import AgentRegistry
        from a2a.agent_loader import load_cybersecsuite_agents

        registry = AgentRegistry()
        load_cybersecsuite_agents(registry)
        agents = registry.summary()

        orchestrators = [a for a in agents if a.get("claude_metadata", {}).get("role") == "orchestrator"]
        specialists = [a for a in agents if a.get("claude_metadata", {}).get("role") != "orchestrator"]

        return {
            "status": "success",
            "total": len(agents),
            "orchestrators": len(orchestrators),
            "specialists": len(specialists),
            "agents": agents,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool(name="cybersec.best_provider")
async def best_provider(
    task: str,
    prefer_free: bool = False,
    max_cost_per_1k: float | None = None,
    require_tools: bool = False,
    require_vision: bool = False,
    min_context: int | None = None,
) -> JsonDict:
    """Recommend the best provider+model for a given task.

    Mirrors OmniRoute's omniroute_best_combo_for_task. Considers cost,
    capabilities (tools, vision, context window), rate limits, and
    circuit breaker state.

    Args:
        task: Description of the task (used for matching)
        prefer_free: Prioritize free providers
        max_cost_per_1k: Maximum cost per 1K tokens (USD)
        require_tools: Only consider models with tool/function calling
        require_vision: Only consider models with vision support
        min_context: Minimum context window size
    """
    from ai_proxy.providers.registry import get_all_providers
    from ai_proxy.routing.combo import get_circuit_breaker_status

    cb_status = get_circuit_breaker_status()
    open_targets = {cb["target"] for cb in cb_status if cb["state"] == "open"}

    candidates = []
    for p in get_all_providers().values():
        if not p.is_available:
            continue
        for m in p.models:
            if m.deprecated:
                continue
            if require_tools and not m.supports_tools:
                continue
            if require_vision and not m.supports_vision:
                continue
            if min_context and m.context_window < min_context:
                continue
            if max_cost_per_1k is not None and m.cost.input > max_cost_per_1k * 1000:
                continue
            if f"{p.id}:{m.id}" in open_targets:
                continue
            candidates.append({
                "provider": p.id,
                "model": m.id,
                "is_free": p.is_free,
                "cost_input": m.cost.input,
                "cost_output": m.cost.output,
                "context_window": m.context_window,
                "supports_tools": m.supports_tools,
                "supports_vision": m.supports_vision,
            })

    if prefer_free:
        candidates.sort(key=lambda c: (not c["is_free"], c["cost_input"]))
    else:
        candidates.sort(key=lambda c: c["cost_input"])

    return {
        "status": "success",
        "task": task,
        "recommended": candidates[0] if candidates else None,
        "alternatives": candidates[1:5],
        "total_candidates": len(candidates),
    }


# ====================== PHASE 0 — CASE OPENING ======================


@mcp.tool(name="cybersec.case_open")
async def case_open_tool(
    title: str,
    problem_statement: str,
    attack_hypothesis: str = "",
    known_facts: list[str] | None = None,
    suspected_iocs: list[str] | None = None,
    affected_assets: list[str] | None = None,
    timeline_hints: list[str] | None = None,
    scope_in: list[str] | None = None,
    scope_out: list[str] | None = None,
    priority: str = "medium",
    mode: str = "blue",
    mitre_hypotheses: list[str] | None = None,
    data_sources: list[str] | None = None,
    tags: list[str] | None = None,
    analyst_notes: str = "",
) -> JsonDict:
    """Open a new investigation case (Phase 0).

    Collects structured facts for threat hunting before any investigation
    phase begins. Creates a CaseIntake record, sets the session phase to
    'case_opening', and populates the SessionLayer with initial hypotheses.

    Args:
        title: Short case title (e.g. "Suspected lateral movement from DC01")
        problem_statement: What happened? What is the user concerned about?
        attack_hypothesis: Initial theory — suspected attack type, vector, or actor
        known_facts: List of confirmed facts (IPs, hashes, timestamps, symptoms)
        suspected_iocs: Preliminary IOC candidates before formal triage
        affected_assets: Hosts, services, accounts, or network segments involved
        timeline_hints: Known timestamps — first seen, last seen, anomaly window
        scope_in: What IS in scope for investigation
        scope_out: What is explicitly OUT of scope
        priority: Case priority (low, medium, high, critical)
        mode: Team posture (blue, red, purple)
        mitre_hypotheses: Suspected MITRE ATT&CK technique IDs (e.g. T1055)
        data_sources: Available data sources (pcaps, logs, disk images, memory dumps)
        tags: Freeform tags for categorization
        analyst_notes: Additional notes from the analyst
    """
    try:
        await init_tortoise_async()
        from db.models.case_intake import CaseIntake
        from db.models.scope import Session, Workspace, Project
        from db.models.layers import SessionLayer

        scope = _get_current_scope()

        # Resolve workspace
        ws, _ = await Workspace.get_or_create(name=scope["workspace"])

        # Resolve project
        proj = None
        if scope.get("project"):
            proj, _ = await Project.get_or_create(
                workspace=ws, name=scope["project"]
            )

        # Resolve session
        sess = None
        if scope.get("session"):
            sess = await Session.get_or_none(session_id=scope["session"])
            if sess:
                sess.phase = "case_opening"
                sess.mode = mode
                await sess.save()

        # Create intake record
        intake = await CaseIntake.create(
            workspace=ws,
            project=proj,
            session=sess,
            title=title,
            problem_statement=problem_statement,
            attack_hypothesis=attack_hypothesis,
            known_facts=known_facts or [],
            suspected_iocs=suspected_iocs or [],
            affected_assets=affected_assets or [],
            timeline_hints=timeline_hints or [],
            scope_in=scope_in or [],
            scope_out=scope_out or [],
            priority=priority,
            mode=mode,
            mitre_hypotheses=mitre_hypotheses or [],
            data_sources=data_sources or [],
            tags=tags or [],
            analyst_notes=analyst_notes,
        )

        # Update SessionLayer with initial hypotheses
        if sess:
            layer, _ = await SessionLayer.get_or_create(
                session=sess,
                defaults={"name": f"phase0-{sess.session_id}"},
            )
            layer.active_phase = "case_opening"
            layer.current_hypotheses = mitre_hypotheses or []
            layer.investigation_focus = affected_assets or []
            layer.analysis_notes = (
                f"Case: {title}\n"
                f"Hypothesis: {attack_hypothesis}\n"
                f"Facts: {'; '.join(known_facts or [])}"
            )
            await layer.save()

        return {
            "status": "success",
            "case_id": intake.id,
            "title": title,
            "priority": priority,
            "mode": mode,
            "phase": "case_opening",
            "facts_count": len(known_facts or []),
            "iocs_count": len(suspected_iocs or []),
            "assets_count": len(affected_assets or []),
            "mitre_count": len(mitre_hypotheses or []),
            "message": f"Case '{title}' opened. Ready for Phase 1 (Recon).",
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool(name="cybersec.case_status")
async def case_status_tool(case_id: int | None = None) -> JsonDict:
    """Get the status of the current or specific case intake.

    Args:
        case_id: Specific case ID, or None for the most recent case.
    """
    try:
        await init_tortoise_async()
        from db.models.case_intake import CaseIntake

        if case_id:
            intake = await CaseIntake.get_or_none(id=case_id)
        else:
            intake = await CaseIntake.all().order_by("-created_at").first()

        if not intake:
            return {"status": "error", "error": "No case found"}

        return {
            "status": "success",
            "case": {
                "id": intake.id,
                "title": intake.title,
                "problem": intake.problem_statement,
                "hypothesis": intake.attack_hypothesis,
                "priority": intake.priority.value if hasattr(intake.priority, "value") else intake.priority,
                "mode": intake.mode.value if hasattr(intake.mode, "value") else intake.mode,
                "known_facts": intake.known_facts,
                "suspected_iocs": intake.suspected_iocs,
                "affected_assets": intake.affected_assets,
                "timeline_hints": intake.timeline_hints,
                "scope_in": intake.scope_in,
                "scope_out": intake.scope_out,
                "mitre_hypotheses": intake.mitre_hypotheses,
                "data_sources": intake.data_sources,
                "tags": intake.tags,
                "opened_by": intake.opened_by,
                "created_at": intake.created_at.isoformat() if intake.created_at else None,
                "closed_at": intake.closed_at.isoformat() if intake.closed_at else None,
            },
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    mcp.run()
