#!/usr/bin/env python3
"""
Shared utilities for cybersecsuite hooks.

Scope layout
────────────
  Global   ~/.claude/                  (LLM-harness config only)
  App      CYBERSECSUITE_HOME          (sessions, memory, vault, cache, logs)
             defaults to ~/.cybersecsuite
  Project  $(pwd)/.claude/             (project harness config only)
  Session  CYBERSECSUITE_HOME/sessions/<sid>/
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# ── Scope roots ───────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(os.environ.get("CYBERSECSUITE_ROOT", Path(__file__).resolve().parent.parent.parent))
HOOKS_DIR    = PROJECT_ROOT / ".claude" / "hooks"
AUDIT_LOG    = HOOKS_DIR / "audit.jsonl"


def get_app_home() -> Path:
    """Return the app-scope home directory (CYBERSECSUITE_HOME, default ~/.cybersecsuite)."""
    return Path(
        os.environ.get("CYBERSECSUITE_HOME", str(Path.home() / ".cybersecsuite"))
    ).expanduser().resolve()


SESSIONS_DIR        = get_app_home() / "sessions"
LEGACY_SESSIONS_DIR = PROJECT_ROOT / ".claude" / "sessions"


def get_project_dir() -> Path:
    return PROJECT_ROOT


def get_memory_dir(layer: str = "") -> Path:
    """Return a memory layer dir inside app home. layer: 'system' | 'project' | 'session' | ''."""
    base = get_app_home() / "memory"
    return base / layer if layer else base


def get_session_dir() -> Optional[Path]:
    session_id = os.environ.get("CYBERSEC_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    if session_id:
        primary = get_app_home() / "sessions" / session_id
        if primary.exists():
            return primary
        legacy = LEGACY_SESSIONS_DIR / session_id
        if legacy.exists():
            return legacy
        primary.mkdir(parents=True, exist_ok=True)
        return primary
    # Fall back to latest session symlink
    latest = get_app_home() / "sessions" / "latest"
    if latest.exists():
        return latest.resolve()
    legacy_latest = LEGACY_SESSIONS_DIR / "latest"
    if legacy_latest.exists():
        return legacy_latest.resolve()
    return None


def ensure_structure() -> None:
    app = get_app_home()
    for d in [
        HOOKS_DIR,
        app / "sessions",
        app / "memory" / "system",
        app / "memory" / "project",
        app / "memory" / "session",
        app / "vault",
        app / "cache",
        app / "logs",
    ]:
        d.mkdir(parents=True, exist_ok=True)


def append_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)


def audit(event: dict) -> None:
    event.setdefault("ts", datetime.now(timezone.utc).isoformat())
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    append_file(AUDIT_LOG, json.dumps(event) + "\n")


def read_stdin() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def emit(output: dict) -> None:
    print(json.dumps(output))


def hook_context(text: str) -> dict:
    """Wrap text as a Claude hook additionalContext output."""
    return {"hookSpecificOutput": {"additionalContext": text}}


def count_lines(path: Path, pattern: str) -> int:
    """Count lines matching a regex pattern in a file."""
    import re
    if not path.exists():
        return 0
    try:
        return sum(1 for ln in path.read_text("utf-8").splitlines() if re.match(pattern, ln))
    except Exception:
        return 0


SEVERITY_EMOJI = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}
