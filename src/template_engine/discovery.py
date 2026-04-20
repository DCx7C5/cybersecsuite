"""Scope-aware template path discovery.

Searches for a template by name in priority order: session → project → app → global.
First match wins (highest-priority scope).
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def _template_search_dirs(
    project_dir: Path | None = None,
    session_id: str | None = None,
    global_dir: Path | None = None,
    app_dir: Path | None = None,
) -> list[Path]:
    """Return template directories in descending priority (highest first)."""
    if global_dir is None:
        global_dir = Path("~/.claude").expanduser()
    if app_dir is None:
        app_dir = Path("~/.cybersecsuite").expanduser()
    if project_dir is None:
        project_dir = Path.cwd()

    claude_dir = project_dir / ".claude"

    # Session dir (highest priority)
    sid = session_id or os.environ.get("CYBERSEC_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    session_dir: Path | None = None
    if sid:
        session_dir = claude_dir / "sessions" / sid
    else:
        latest = claude_dir / "sessions" / "latest"
        if latest.is_symlink() or latest.is_dir():
            session_dir = latest

    dirs: list[Path] = []
    if session_dir:
        dirs.append(session_dir / "templates")
    dirs.append(claude_dir / "templates")
    dirs.append(app_dir / "templates")
    dirs.append(global_dir / "templates")

    return dirs


def resolve_template(
    name: str,
    project_dir: Path | None = None,
    session_id: str | None = None,
    global_dir: Path | None = None,
    app_dir: Path | None = None,
) -> Path | None:
    """Find the highest-priority file matching `name`.

    `name` may be a relative path like ``"reports/investigation-report.md"``
    or a bare filename like ``"artifact.md"``.
    """
    dirs = _template_search_dirs(
        project_dir=project_dir,
        session_id=session_id,
        global_dir=global_dir,
        app_dir=app_dir,
    )
    for d in dirs:
        candidate = d / name
        if candidate.exists():
            return candidate
    return None


def list_templates(
    project_dir: Path | None = None,
    session_id: str | None = None,
    global_dir: Path | None = None,
    app_dir: Path | None = None,
) -> list[dict]:
    """List all discoverable templates with scope metadata."""
    dirs = _template_search_dirs(
        project_dir=project_dir,
        session_id=session_id,
        global_dir=global_dir,
        app_dir=app_dir,
    )
    scope_names = ["session", "project", "app", "global"]
    seen: set[str] = set()
    results: list[dict] = []

    for scope, d in zip(scope_names, dirs):
        if not d.exists():
            continue
        for p in sorted(d.rglob("*")):
            if not p.is_file():
                continue
            rel = str(p.relative_to(d))
            if rel not in seen:
                seen.add(rel)
                results.append({
                    "name": rel,
                    "scope": scope,
                    "path": str(p),
                })

    return results


def discover_skills(
    domain: str | None = None,
    project_dir: Path | None = None,
) -> list[dict]:
    """Discover skills from .claude/skills/ directory."""
    global_dir = Path("~/.claude").expanduser()
    app_dir = Path("~/.cybersecsuite").expanduser()
    if project_dir is None:
        project_dir = Path.cwd()

    skills_dir = global_dir / "skills"
    index_file = global_dir / "skills-index.json"

    results: list[dict] = []

    if index_file.exists():
        try:
            index = json.loads(index_file.read_text())
            skills = index.get("skills", [])
            for s in skills:
                if domain is None or s.get("domain") == domain:
                    results.append(s)
            return results
        except Exception:
            pass

    if skills_dir.exists():
        for p in sorted(skills_dir.rglob("SKILL.md")):
            name = p.parent.name
            rel = str(p.parent.relative_to(skills_dir))
            if domain and not rel.startswith(domain):
                continue
            results.append({
                "name": name,
                "path": str(p),
                "domain": rel.split("/")[0] if "/" in rel else "other",
            })

    return results
