"""Shared scope helpers for src/mcp/cybersec/ SDK tools.

Extracted from mcp_server.py (lines 16-142) for reuse across tool modules.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Final, TypedDict

# Make hooks available (PYTHONPATH equivalent for package context)
_AI_HOOKS_DIR = os.environ.get("CYBERSEC_AI_HOOKS_DIR", "/home/daen/Projects/AI")
if _AI_HOOKS_DIR not in sys.path:
    sys.path.insert(0, _AI_HOOKS_DIR)

JsonDict = dict[str, Any]


class ScopeState(TypedDict):
    workspace: str
    project: str | None
    session: str | None


FINDING_SEVERITIES: Final[tuple[str, ...]] = ("low", "medium", "high", "critical")
FINDING_STATUSES: Final[tuple[str, ...]] = (
    "open", "investigating", "confirmed", "false_positive", "resolved", "accepted_risk",
)
IOC_STATUSES: Final[tuple[str, ...]] = ("active", "cleared", "watchlist", "expired")
CONFIDENCE_LEVELS: Final[tuple[str, ...]] = ("low", "medium", "high", "confirmed")
SCOPE_LEVELS: Final[tuple[str, ...]] = ("workspace", "project", "session")


def _get_base_dir() -> Path:
    base_dir = os.environ.get("CYBERSEC_BASE_DIR") or os.environ.get("MALWAREHUNTER_BASE_DIR")
    if base_dir:
        return Path(base_dir).expanduser().resolve()
    plugin_data_dir = os.environ.get("PLUGIN_DATA_DIR") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if plugin_data_dir:
        return Path(plugin_data_dir).expanduser().resolve() / "cybersec"
    return Path(__file__).resolve().parents[3] / "data"


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
            raise ValueError(f"Unsupported scope '{item}'. Allowed: {', '.join(SCOPE_LEVELS)}")
        if scope_name not in normalized:
            normalized.append(scope_name)
    return normalized or list(SCOPE_LEVELS)


def _normalize_scope_level(value: Any, default: str = "project") -> str:
    normalized = str(value).strip().lower() if value is not None else default
    if normalized not in SCOPE_LEVELS:
        raise ValueError(f"Unsupported scope '{normalized}'. Allowed: {', '.join(SCOPE_LEVELS)}")
    return normalized


def sdk_result(data: JsonDict | str) -> JsonDict:
    """Wrap a result dict into SDK content format."""
    text = data if isinstance(data, str) else json.dumps(data, default=str)
    return {"content": [{"type": "text", "text": text}]}


def sdk_error(message: str) -> JsonDict:
    """Return an SDK error result."""
    return {
        "content": [{"type": "text", "text": json.dumps({"status": "error", "error": message})}],
        "isError": True,
    }


def _build_scope_context(scope: ScopeState) -> Any:
    """Build a ScopeContext from env-resolved scope state. Lazy import to avoid hard dep."""
    try:
        from hooks.database import ScopeContext
        return ScopeContext(
            workspace_name=scope["workspace"],
            project_name=scope["project"],
            session_id=scope["session"],
        )
    except ImportError:
        return scope
