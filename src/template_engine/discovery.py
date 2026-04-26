"""Scope-aware template path discovery.

Searches for a template by name in priority order: session → project → app → global.
First match wins (highest-priority scope).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from template_engine.session_scope import legacy_project_sessions_dir, project_sessions_dir


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
    sessions_dir = project_sessions_dir(project_dir)
    legacy_sessions_dir = legacy_project_sessions_dir(project_dir)

    # Session dir (highest priority)
    sid = session_id or os.environ.get("CYBERSEC_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    session_dirs: list[Path] = []
    if sid:
        primary = sessions_dir / sid
        legacy = legacy_sessions_dir / sid
        if primary.exists():
            session_dirs.append(primary)
        if legacy.exists() and legacy != primary:
            session_dirs.append(legacy)
        if not session_dirs:
            session_dirs.append(primary)
    else:
        latest = sessions_dir / "latest"
        if latest.is_symlink() or latest.is_dir():
            session_dirs.append(latest)
        else:
            legacy_latest = legacy_sessions_dir / "latest"
            if legacy_latest.is_symlink() or legacy_latest.is_dir():
                session_dirs.append(legacy_latest)

    dirs: list[Path] = []
    for session_dir in session_dirs:
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
    """Discover skills from multiple locations (marketplace, .claude/skills, etc).
    
    Search order (highest priority first):
    1. AI Marketplace: /home/daen/Projects/ai-marketplace/skills/
    2. User global: ~/.claude/skills/
    3. Fallback: Look for skills-index.json
    """
    global_dir = Path("~/.claude").expanduser()
    if project_dir is None:
        project_dir = Path.cwd()

    # Primary locations to search (highest to lowest priority)
    marketplace_dir = Path("/home/daen/Projects/ai-marketplace/skills")
    marketplace_index = marketplace_dir / "index.json"
    skills_dir = global_dir / "skills"
    index_file = global_dir / "skills-index.json"

    results: list[dict] = []
    seen_ids: set[str] = set()

    def add_skill(skill_data: dict) -> None:
        """Add skill to results, avoiding duplicates."""
        skill_id = skill_data.get("id") or skill_data.get("path", "")
        if skill_id not in seen_ids:
            results.append(skill_data)
            seen_ids.add(skill_id)

    # 1. Try marketplace index first (highest priority)
    if marketplace_index.exists():
        try:
            index = json.loads(marketplace_index.read_text())
            skills = index.get("skills", [])
            for s in skills:
                if domain is None or s.get("category", "").startswith(domain):
                    add_skill(s)
            if results:
                return results  # Use marketplace skills exclusively
        except Exception:
            pass

    # 2. Try marketplace directory (if index not found)
    if marketplace_dir.exists() and not results:
        for p in sorted(marketplace_dir.rglob("SKILL.md")):
            name = p.parent.name
            rel = str(p.parent.relative_to(marketplace_dir))
            if domain and not rel.startswith(domain):
                continue
            add_skill({
                "name": name,
                "path": str(p),
                "domain": rel.split("/")[0] if "/" in rel else "other",
                "source": "marketplace",
            })

    # 3. Try user index
    if index_file.exists():
        try:
            index = json.loads(index_file.read_text())
            skills = index.get("skills", [])
            for s in skills:
                if domain is None or s.get("domain") == domain:
                    add_skill(s)
        except Exception:
            pass

    # 4. Try user skills directory
    if skills_dir.exists():
        for p in sorted(skills_dir.rglob("SKILL.md")):
            name = p.parent.name
            rel = str(p.parent.relative_to(skills_dir))
            if domain and not rel.startswith(domain):
                continue
            add_skill({
                "name": name,
                "path": str(p),
                "domain": rel.split("/")[0] if "/" in rel else "other",
                "source": "user",
            })

    return results
