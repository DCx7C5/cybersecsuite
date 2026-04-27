"""Thin context wrapper — avoids circular imports between sdk.py and session_scope."""
from __future__ import annotations

import copy
import json as _json
import os
from pathlib import Path
from typing import Any

try:
    import yaml
    _YAML = True
except ImportError:
    _YAML = False


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
        if _YAML and path.suffix in (".yaml", ".yml"):
            result = yaml.safe_load(text) or {}
        else:
            result = _json.loads(text)
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def _deep_merge(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = copy.deepcopy(val)
    return result


def _scope_dirs(project_dir, session_id, global_dir, app_dir) -> list[Path]:
    from cybersecsuite.session_scope import legacy_project_sessions_dir, project_sessions_dir
    if global_dir is None:
        global_dir = Path("~/.claude").expanduser()
    if app_dir is None:
        app_dir = Path("~/.cybersecsuite").expanduser()
    if project_dir is None:
        project_dir = Path.cwd()
    claude_dir = project_dir / ".claude"
    sessions_dir = project_sessions_dir(project_dir)
    legacy_sessions_dir = legacy_project_sessions_dir(project_dir)
    dirs = [global_dir, app_dir, claude_dir]
    sid = session_id or os.environ.get("CYBERSEC_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    if sid:
        legacy_session = legacy_sessions_dir / sid
        if legacy_session.exists() and legacy_session != (sessions_dir / sid):
            dirs.append(legacy_session)
        dirs.append(sessions_dir / sid)
    else:
        latest = sessions_dir / "latest"
        if latest.is_symlink() or latest.is_dir():
            dirs.append(latest)
        else:
            legacy_latest = legacy_sessions_dir / "latest"
            if legacy_latest.is_symlink() or legacy_latest.is_dir():
                dirs.append(legacy_latest)
    return dirs


def get_context(
    project_dir: Path | None = None,
    session_id: str | None = None,
    global_dir: Path | None = None,
    app_dir: Path | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    dirs = _scope_dirs(project_dir=project_dir, session_id=session_id, global_dir=global_dir, app_dir=app_dir)
    merged: dict[str, Any] = {}
    for d in dirs:
        for name in ("context.yaml", "context.yml", "context.json"):
            layer = _load_yaml(d / name)
            if layer:
                merged = _deep_merge(merged, layer)
                break
    if extra:
        merged = _deep_merge(merged, extra)
    return merged
