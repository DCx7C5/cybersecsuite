#!/usr/bin/env python3
"""
Shared utilities for cybersecsuite Claude hooks.
Replaces the old utils/ from the AI plugin with cybersecsuite-native paths and DB.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# ── Project layout ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(os.environ.get("CYBERSECSUITE_ROOT", Path(__file__).resolve().parent.parent.parent))
HOOKS_DIR    = PROJECT_ROOT / ".claude" / "hooks"
SESSIONS_DIR = PROJECT_ROOT / ".claude" / "sessions"
AUDIT_LOG    = HOOKS_DIR / "audit.jsonl"


def get_project_dir() -> Path:
    return PROJECT_ROOT


def get_session_dir() -> Optional[Path]:
    session_id = os.environ.get("CYBERSEC_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    if session_id:
        d = SESSIONS_DIR / session_id
        d.mkdir(parents=True, exist_ok=True)
        return d
    # Fall back to latest session symlink
    latest = SESSIONS_DIR / "latest"
    if latest.exists():
        return latest.resolve()
    return None


def ensure_structure() -> None:
    for d in [HOOKS_DIR, SESSIONS_DIR]:
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

