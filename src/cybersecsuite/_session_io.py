"""Session I/O helpers — read/write session-manifest.json and .last_session pointer."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_manifest(session_dir: Path) -> dict[str, Any]:
    """Read session-manifest.json; return {} if absent or corrupt."""
    path = session_dir / "session-manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_manifest(session_dir: Path, data: dict[str, Any]) -> None:
    """Write session-manifest.json atomically."""
    session_dir.mkdir(parents=True, exist_ok=True)
    path = session_dir / "session-manifest.json"
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def read_last_session(sessions_dir: Path) -> dict[str, Any] | None:
    """Read .last_session pointer file; return None if absent."""
    path = sessions_dir / ".last_session"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def write_last_session(sessions_dir: Path, name: str, session_dir: Path) -> None:
    """Write .last_session JSON pointer."""
    sessions_dir.mkdir(parents=True, exist_ok=True)
    path = sessions_dir / ".last_session"
    path.write_text(json.dumps({
        "name": name,
        "path": str(session_dir),
        "suspended_at": _now(),
    }, indent=2), encoding="utf-8")


def update_latest_symlink(sessions_dir: Path, session_dir: Path) -> None:
    """Update the 'latest' symlink to point at session_dir."""
    latest = sessions_dir / "latest"
    try:
        if latest.is_symlink() or latest.exists():
            latest.unlink()
        os.symlink(session_dir.name, latest)
    except OSError:
        pass  # non-fatal: hooks fall back to env var


def new_session_id() -> str:
    return str(uuid.uuid4())
