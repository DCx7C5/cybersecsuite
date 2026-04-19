"""Jinja2 rendering engine with 4-scope template search and custom filters.

Environment settings:
- FileSystemLoader searches session → project → app → global (first match wins)
- UndefinedError is silenced: missing vars render as empty string and log a warning
- Custom filters: severity_badge, mitre_format, now_utc
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    Undefined,
    UndefinedError,
)

logger = logging.getLogger(__name__)


class _SilentUndefined(Undefined):
    """Log a warning and return empty string for undefined variables."""

    def __str__(self) -> str:
        logger.warning("template_engine: undefined variable %r", self._undefined_name)
        return ""

    def __repr__(self) -> str:  # pragma: no cover
        return ""

    def __iter__(self):  # pragma: no cover
        return iter([])

    def __bool__(self) -> bool:  # pragma: no cover
        return False


# ── Custom filters ────────────────────────────────────────────────────────────

def _severity_badge(value: str) -> str:
    """Render a severity string as an uppercase badge label."""
    v = str(value).upper()
    colours = {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "yellow", "LOW": "blue", "INFO": "grey"}
    colour = colours.get(v, "grey")
    return f"[{colour.upper()}:{v}]"


def _mitre_format(value: str) -> str:
    """Normalise a MITRE technique identifier to uppercase (e.g. t1055 → T1055)."""
    return str(value).upper()


def _now_utc(fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> str:
    """Return current UTC time as formatted string."""
    return datetime.now(timezone.utc).strftime(fmt)


# ── Engine factory ────────────────────────────────────────────────────────────

def _build_loaders(
    project_dir: Path | None,
    session_id: str | None,
    global_dir: Path | None,
    app_dir: Path | None,
) -> list[FileSystemLoader]:
    """Build FileSystemLoader list in priority order (highest first)."""
    if global_dir is None:
        global_dir = Path("~/.claude").expanduser()
    if app_dir is None:
        app_dir = Path("~/.cybersecsuite").expanduser()
    if project_dir is None:
        project_dir = Path.cwd()

    claude_dir = project_dir / ".claude"

    sid = session_id or os.environ.get("CYBERSEC_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    session_tpl_dir: Path | None = None
    if sid:
        session_tpl_dir = claude_dir / "sessions" / sid / "templates"
    else:
        latest = claude_dir / "sessions" / "latest"
        if latest.is_symlink() or latest.is_dir():
            session_tpl_dir = latest / "templates"

    dirs: list[Path] = []
    if session_tpl_dir:
        dirs.append(session_tpl_dir)
    dirs.append(claude_dir / "templates")
    dirs.append(app_dir / "templates")
    dirs.append(global_dir / "templates")

    return [FileSystemLoader(str(d)) for d in dirs if d.exists()]


def build_environment(
    project_dir: Path | None = None,
    session_id: str | None = None,
    global_dir: Path | None = None,
    app_dir: Path | None = None,
) -> Environment:
    """Build and return a configured Jinja2 Environment."""
    loaders = _build_loaders(
        project_dir=project_dir,
        session_id=session_id,
        global_dir=global_dir,
        app_dir=app_dir,
    )
    loader = ChoiceLoader(loaders) if loaders else ChoiceLoader([])
    env = Environment(
        loader=loader,
        undefined=_SilentUndefined,
        autoescape=False,
        keep_trailing_newline=True,
    )
    env.filters["severity_badge"] = _severity_badge
    env.filters["mitre_format"] = _mitre_format
    env.globals["now_utc"] = _now_utc
    return env


def render(
    template_name: str,
    ctx: dict[str, Any],
    project_dir: Path | None = None,
    session_id: str | None = None,
    global_dir: Path | None = None,
    app_dir: Path | None = None,
) -> str:
    """Render a named template with the given context dict.

    Searches scopes in priority order: session → project → app → global.
    Raises TemplateNotFound if no matching template is found in any scope.
    """
    env = build_environment(
        project_dir=project_dir,
        session_id=session_id,
        global_dir=global_dir,
        app_dir=app_dir,
    )
    tpl = env.get_template(template_name)
    return tpl.render(**ctx)


def render_string(
    source: str,
    ctx: dict[str, Any],
    project_dir: Path | None = None,
    session_id: str | None = None,
    global_dir: Path | None = None,
    app_dir: Path | None = None,
) -> str:
    """Render an inline Jinja2 template string with the given context."""
    env = build_environment(
        project_dir=project_dir,
        session_id=session_id,
        global_dir=global_dir,
        app_dir=app_dir,
    )
    tpl = env.from_string(source)
    return tpl.render(**ctx)
