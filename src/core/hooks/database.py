#!/usr/bin/env python3
"""
CyberSec Database Layer — PostgreSQL via Tortoise ORM with two-tier scope system.

Scope hierarchy: project → session with proper relationships.
Database is automatically created on first start. Fully async-native with
Tortoise ORM and uvloop optimization.
"""
import asyncio
import hashlib
import json
import os
from datetime import datetime
from typing import Any, Optional, List, cast

# Import uvloop integration for performance boost
try:
    from hooks.uvloop_integration import run_with_uvloop
except ImportError:  # pragma: no cover - direct script execution fallback
    import asyncio as _asyncio

    def run_with_uvloop(coro):  # type: ignore[misc]
        return _asyncio.run(coro)

# Bootstrap Tortoise ORM lazily to avoid import-time DB failures
from db.bootstrap import init_tortoise_async

from db.models.scope import ProjectScope, SessionScope
from db.models.investigation import (
    Finding,
    IOC,
    Risk,
    MITRETechnique,
    Baseline,
    WatchlistItem,
    SharedEntry
)
from db.models.enums import (
    Severity,
    FindingStatus,
    IOCStatus,
    Confidence,
    WatchlistPriority,
    BaselineDomain
)

# ========================= SCOPE MANAGEMENT =========================

_db_init_lock: asyncio.Lock | None = None


def _get_db_init_lock() -> asyncio.Lock:
    global _db_init_lock
    if _db_init_lock is None:
        _db_init_lock = asyncio.Lock()
    return cast(asyncio.Lock, _db_init_lock)


def _should_auto_create_db() -> bool:
    return os.environ.get("CYBERSEC_AUTO_CREATE_DB", "").strip().lower() in {"1", "true", "yes", "on"}


async def ensure_database_initialized(create_db: bool | None = None) -> None:
    """Initialize Tortoise lazily so imports do not require a live database."""
    async with _get_db_init_lock():
        await init_tortoise_async(create_db=_should_auto_create_db() if create_db is None else create_db)

async def get_or_create_project_async(
    project_name: str,
    description: str = "",
    path: str = ""
) -> ProjectScope:
    """Get or create a project by name."""
    await ensure_database_initialized()
    project = await ProjectScope.filter(name=project_name).first()
    if not project:
        project = await ProjectScope.create(
            name=project_name,
            description=description,
            path=path
        )
    return project


async def get_or_create_session_async(
    project_name: str,
    session_id: str,
    name: str = "",
    description: str = "",
    path: str = "",
    agent: str = ""
) -> SessionScope:
    """Get or create a session within a project."""
    project = await get_or_create_project_async(project_name)
    session = await SessionScope.filter(session_id=session_id).first()
    if not session:
        session = await SessionScope.create(
            project=project,
            session_id=session_id,
            name=name or session_id,
            description=description,
            path=path,
            agent=agent
        )
    return session


# ========================= MODEL ROUTING =========================
# Maps value_type strings to Tortoise model classes.

_VALUE_TYPE_MODEL_MAP: dict[str, type] = {
    "finding": Finding,
    "ioc": IOC,
    "risk": Risk,
    "mitre": MITRETechnique,
    "baseline": Baseline,
    "watchlist": WatchlistItem,
}


def _get_model_for_type(value_type: str) -> Any:
    """Return the Tortoise model for a value_type, or SharedEntry as fallback."""
    return _VALUE_TYPE_MODEL_MAP.get(value_type, SharedEntry)


# ========================= SCOPE CONTEXT =========================

class ScopeContext:
    """Context object to track current project/session scope."""

    def __init__(
        self,
        project_name: str | None = None,
        session_id: str | None = None
    ):
        self.project_name = project_name
        self.session_id = session_id
        self._project: Optional[ProjectScope] = None
        self._session: Optional[SessionScope] = None

    async def resolve_scope_async(self):
        """Resolve project/session objects."""
        if self.project_name:
            self._project = await get_or_create_project_async(self.project_name)

        if self.session_id and self.project_name:
            self._session = await get_or_create_session_async(
                self.project_name,
                self.session_id
            )

    @property
    def project(self) -> Optional[ProjectScope]:
        return self._project

    @property
    def session(self) -> Optional[SessionScope]:
        return self._session


# ========================= ASYNC WRITE =========================

async def write_entry_async(
    scope: ScopeContext,
    value_type: str,
    data: dict[str, Any]
) -> dict[str, Any]:
    """
    Write data to the appropriate model asynchronously with three-tier scope.

    Args:
        scope: ScopeContext defining workspace/project/session
        value_type: Type of data (finding, ioc, risk, etc.)
        data: Data to write
    """
    await scope.resolve_scope_async()
    model = _get_model_for_type(value_type)

    if model is SharedEntry:
        return await _write_shared_entry_async(scope, value_type, data)

    # Route to specific model handlers
    if model is Finding:
        return await _write_finding_async(scope, data)
    if model is IOC:
        return await _write_ioc_async(scope, data)
    if model is Risk:
        return await _write_risk_async(scope, data)
    if model is MITRETechnique:
        return await _write_mitre_async(scope, data)
    if model is Baseline:
        return await _write_baseline_async(scope, data)
    if model is WatchlistItem:
        return await _write_watchlist_async(scope, data)

    return {"status": "error", "message": f"Unhandled model for value_type={value_type}"}


async def _write_shared_entry_async(scope: ScopeContext, value_type: str, data: dict) -> dict:
    """Write generic SharedEntry with scope context."""
    key = (
        data.get("key")
        or data.get("title")
        or data.get("value")
        or str(hash(json.dumps(data, sort_keys=True)))
    )

    # Try to find existing entry in the same scope
    existing = await SharedEntry.filter(
        project=scope.project,
        session=scope.session,
        value_type=value_type,
        key=key
    ).first()

    if existing:
        existing.data = data
        await existing.save()
        return {"status": "success", "scope": scope.project_name, "key": key, "created": False}
    else:
        await SharedEntry.create(
            project=scope.project,
            session=scope.session,
            value_type=value_type,
            key=key,
            data=data
        )
        return {"status": "success", "scope": scope.project_name, "key": key, "created": True}


async def _write_finding_async(scope: ScopeContext, data: dict) -> dict:
    """Write Finding to database with scope context."""
    obj = await Finding.create(
        project=scope.project,
        session=scope.session,
        title=data.get("title", "Untitled"),
        description=data.get("description", ""),
        severity=data.get("severity", Severity.MEDIUM),
        status=data.get("status", FindingStatus.OPEN),
        confidence=data.get("confidence", Confidence.MEDIUM),
        location=data.get("location", ""),
        tags=data.get("tags", []),
    )
    return {"status": "success", "scope": scope.project_name, "id": obj.id, "key": obj.title}


async def _write_ioc_async(scope: ScopeContext, data: dict) -> dict:
    """Write IOC to database with scope context."""
    ioc_type = data.get("ioc_type", data.get("type", "unknown"))
    value = data.get("value", "")
    ioc_id = data.get("ioc_id") or _build_ioc_id(ioc_type, value)

    # Try to find existing IOC in the same project
    existing = await IOC.filter(
        project=scope.project,
        ioc_type=ioc_type,
        value=value
    ).first()

    if existing:
        # Update existing IOC
        existing.confidence = data.get("confidence", existing.confidence)
        existing.status = data.get("status", existing.status)
        existing.context = data.get("context", existing.context)
        existing.first_session_id = data.get("first_session_id", existing.first_session_id)
        existing.last_session_id = data.get("last_session_id", existing.last_session_id)
        existing.sightings += 1
        await existing.save()
        return {"status": "success", "scope": scope.project_name, "id": existing.id, "key": value, "created": False}
    else:
        # Create new IOC
        obj = await IOC.create(
            project=scope.project,
            session=scope.session,
            ioc_id=ioc_id,
            ioc_type=ioc_type,
            value=value,
            confidence=data.get("confidence", Confidence.LOW),
            status=data.get("status", IOCStatus.ACTIVE),
            context=data.get("context", {}),
            source=data.get("source", ""),
            tags=data.get("tags", []),
            first_session_id=data.get("first_session_id", scope.session_id or ""),
            last_session_id=data.get("last_session_id", scope.session_id or ""),
            sightings=1,
        )
        return {"status": "success", "scope": scope.project_name, "id": obj.id, "key": value, "created": True}


def _build_ioc_id(ioc_type: str, value: str) -> str:
    """Create a stable IOC identifier when callers do not provide one."""
    normalized_type = (ioc_type or "ioc").strip().upper().replace(" ", "_")[:16] or "IOC"
    digest = hashlib.sha1(f"{ioc_type}:{value}".encode("utf-8")).hexdigest()[:16]
    return f"{normalized_type}-{digest}"


async def _write_risk_async(scope: ScopeContext, data: dict) -> dict:
    """Write Risk to database with scope context."""
    risk_id = data.get("risk_id", f"RISK-{int(datetime.now().timestamp())}")

    # Try to find existing risk
    existing = await Risk.filter(
        project=scope.project,
        risk_id=risk_id
    ).first()

    if existing:
        existing.impact = data.get("impact", existing.impact)
        existing.likelihood = data.get("likelihood", existing.likelihood)
        existing.mitigation = data.get("mitigation", existing.mitigation)
        await existing.save()
        return {"status": "success", "scope": scope.project_name, "id": existing.id, "key": risk_id, "created": False}
    else:
        obj = await Risk.create(
            project=scope.project,
            session=scope.session,
            risk_id=risk_id,
            impact=data.get("impact", ""),
            likelihood=data.get("likelihood", ""),
            mitigation=data.get("mitigation", ""),
        )
        return {"status": "success", "scope": scope.project_name, "id": obj.id, "key": risk_id, "created": True}


async def _write_mitre_async(scope: ScopeContext, data: dict) -> dict:
    """Write MITRE technique to database with scope context."""
    technique_id = data.get("technique_id", "")

    obj = await MITRETechnique.create(
        project=scope.project,
        session=scope.session,
        technique_id=technique_id,
        name=data.get("name", ""),
        description=data.get("description", ""),
        tactic=data.get("tactic", data.get("category", "")),
    )
    return {"status": "success", "scope": scope.project_name, "id": obj.id, "key": technique_id}


async def _write_baseline_async(scope: ScopeContext, data: dict) -> dict:
    """Write Baseline to database with scope context."""
    domain = data.get("domain", BaselineDomain.NETWORK)

    # Try to find existing baseline
    existing = await Baseline.filter(
        project=scope.project,
        domain=domain
    ).first()

    if existing:
        existing.snapshot_data = data.get("snapshot_data", existing.snapshot_data)
        existing.confirmed_clean = data.get("confirmed_clean", existing.confirmed_clean)
        await existing.save()
        return {"status": "success", "scope": scope.project_name, "id": existing.id, "key": domain, "created": False}
    else:
        obj = await Baseline.create(
            project=scope.project,
            session=scope.session,
            domain=domain,
            snapshot_data=data.get("snapshot_data", {}),
            session_ref=data.get("session_ref", scope.session_id or ""),
            confirmed_clean=data.get("confirmed_clean", False),
        )
        return {"status": "success", "scope": scope.project_name, "id": obj.id, "key": domain, "created": True}


async def _write_watchlist_async(scope: ScopeContext, data: dict) -> dict:
    """Write WatchlistItem to database with scope context."""
    obj = await WatchlistItem.create(
        project=scope.project,
        session=scope.session,
        item_type=data.get("item_type", "unknown"),
        value_pattern=data.get("value_pattern", ""),
        reason=data.get("reason", ""),
        priority=data.get("priority", WatchlistPriority.MEDIUM),
        added_by_session_id=data.get("added_by_session_id", scope.session_id or ""),
    )
    return {"status": "success", "scope": scope.project_name, "id": obj.id, "key": obj.value_pattern}


# ========================= ASYNC READ =========================

async def get_entries_async(scope: ScopeContext, value_type: str, limit: int = 100) -> List[dict]:
    """Get entries from database with scope filtering."""
    await scope.resolve_scope_async()
    model = cast(Any, _get_model_for_type(value_type))

    if model is SharedEntry:
        query = _scope_filtered_query(SharedEntry, scope).filter(value_type=value_type)
        entries = await query.limit(limit).all()
        return [{"id": e.id, "key": e.key, "data": e.data, "created_at": e.created_at} for e in entries]

    entries = await _scope_filtered_query(model, scope).limit(limit).all()
    return [_model_to_dict(entry) for entry in entries]


async def query_findings_db_async(
    scope: ScopeContext,
    severity: str = None,
    status: str = None,
    limit: int = 100
) -> List[dict]:
    """Query findings with optional filters."""
    await scope.resolve_scope_async()

    query = _scope_filtered_query(Finding, scope)
    if severity:
        query = query.filter(severity=severity)
    if status:
        query = query.filter(status=status)

    findings = await query.limit(limit).all()
    return [_model_to_dict(finding) for finding in findings]


async def get_recent_entries_async(scope: ScopeContext, limit: int = 20) -> List[dict]:
    """Get recent entries across all types in scope."""
    await scope.resolve_scope_async()

    # Get recent entries from all models
    recent_entries = []

    for model in [Finding, IOC, Risk, MITRETechnique, Baseline, WatchlistItem]:
        entries = await _scope_filtered_query(model, scope).order_by("-updated_at").limit(limit // 6).all()
        recent_entries.extend([_model_to_dict(entry) for entry in entries])

    # Sort by updated_at and limit
    recent_entries.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return recent_entries[:limit]


def _model_to_dict(obj) -> dict:
    """Convert Tortoise model instance to dictionary."""
    result = {}
    for field_name in obj._meta.fields:
        value = getattr(obj, field_name, None)
        if isinstance(value, datetime):
            result[field_name] = value.isoformat()
        else:
            result[field_name] = value
    return result


def _scope_filtered_query(model: Any, scope: ScopeContext) -> Any:
    """Apply project/session filters to a Tortoise model query."""
    if scope.project:
        query = model.filter(project=scope.project)
    else:
        query = model.all()
    if scope.session:
        query = query.filter(session=scope.session)
    return query


# ========================= SYNC WRAPPERS FOR BACKWARD COMPATIBILITY =========================

def _write_entry_scoped_sync(scope_dict: dict, value_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Sync wrapper for write_entry_async using scope dictionary.

    Args:
        scope_dict: Dict with 'project', 'session' keys
        value_type: Type of data
        data: Data to write
    """
    scope = ScopeContext(
        project_name=scope_dict.get("project"),
        session_id=scope_dict.get("session")
    )
    return run_with_uvloop(write_entry_async(scope, value_type, data))


def _get_entries_scoped_sync(scope_dict: dict, value_type: str, limit: int = 100) -> List[dict]:
    """Sync wrapper for get_entries_async."""
    scope = ScopeContext(
        project_name=scope_dict.get("project"),
        session_id=scope_dict.get("session")
    )
    return run_with_uvloop(get_entries_async(scope, value_type, limit))


def query_findings_db_sync(scope_dict: dict, **kwargs) -> List[dict]:
    """Sync wrapper for query_findings_db_async."""
    scope = ScopeContext(
        project_name=scope_dict.get("project"),
        session_id=scope_dict.get("session")
    )
    return run_with_uvloop(query_findings_db_async(scope, **kwargs))


# ========================= LEGACY COMPATIBILITY =========================
# Maintain old layer-based API for backward compatibility

def write_entry_legacy_sync(layer: str, value_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """Legacy layer-based API - maps layers to default scope structure."""
    if layer == "session":
        scope_dict = {"project": "default", "session": "current"}
    else:
        scope_dict = {"project": "default"}

    return _write_entry_scoped_sync(scope_dict, value_type, data)


def get_entries_legacy_sync(layer: str, value_type: str, limit: int = 100) -> List[dict]:
    """Legacy layer-based API - maps layers to default scope structure."""
    if layer == "session":
        scope_dict = {"project": "default", "session": "current"}
    else:
        scope_dict = {"project": "default"}

    return _get_entries_scoped_sync(scope_dict, value_type, limit)


def write_entry_sync(layer: str, value_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """Public legacy-compatible write API."""
    return write_entry_legacy_sync(layer, value_type, data)


def get_entries_sync(layer: str, value_type: str, limit: int = 100) -> List[dict]:
    """Public legacy-compatible read API."""
    return get_entries_legacy_sync(layer, value_type, limit)


# ========================= MAIN SCOPE API =========================
# New API functions that use the three-tier scope system directly

async def write_scoped_entry_async(
    project_name: str = None,
    session_id: str = None,
    value_type: str = "",
    data: dict = None
) -> dict:
    """
    Primary API for writing scoped entries.

    Args:
        project_name: Optional project name
        session_id: Optional session ID
        value_type: Type of data (finding, ioc, etc.)
        data: Data to write
    """
    scope = ScopeContext(project_name, session_id)
    return await write_entry_async(scope, value_type, data or {})


async def get_scoped_entries_async(
    project_name: str = None,
    session_id: str = None,
    value_type: str = "",
    limit: int = 100
) -> List[dict]:
    """
    Primary API for reading scoped entries.

    Args:
        project_name: Optional project name
        session_id: Optional session ID
        value_type: Type of data to query
        limit: Maximum number of results
    """
    scope = ScopeContext(project_name, session_id)
    return await get_entries_async(scope, value_type, limit)