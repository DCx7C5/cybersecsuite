"""Session scope path helpers.

SDK sessions live under:
    $(project)/.<scope>/sessions/<session_id>

The scope name is controlled by CYBERSEC_SESSION_SCOPE.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

DEFAULT_SESSION_SCOPE = "cybersec"


def resolve_session_scope_name(scope_name: str | None = None) -> str:
    """Return a normalized session scope name without a leading dot."""
    raw = (scope_name or os.environ.get("CYBERSEC_SESSION_SCOPE", DEFAULT_SESSION_SCOPE)).strip()
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "", raw.lstrip("."))
    return cleaned or DEFAULT_SESSION_SCOPE


def project_session_scope_dir(project_dir: Path, scope_name: str | None = None) -> Path:
    return project_dir / f".{resolve_session_scope_name(scope_name)}"


def project_sessions_dir(project_dir: Path, scope_name: str | None = None) -> Path:
    return project_session_scope_dir(project_dir, scope_name) / "sessions"


def legacy_project_sessions_dir(project_dir: Path) -> Path:
    """Legacy location kept for backward-compatible reads."""
    return project_dir / ".claude" / "sessions"
