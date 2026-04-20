"""CyberSecSuiteSDK — scope and session management.

Usage::

    from cybersecsuite.sdk import CyberSecSuiteSDK

    sdk = CyberSecSuiteSDK()

    # Open (or resume) a named session — writes go to .<scope>/sessions/<name>/
    # where <scope> comes from CYBERSEC_SESSION_SCOPE (default: "cybersec")
    with sdk.session(name="apt29-hunt"):
        sdk.set_pov("hunter")
        sdk.set("mitre_tactic", "Persistence")
        output = sdk.render("reports/investigation-report.md")

    # Resume the last suspended session
    last = sdk.last_session()   # → SessionInfo | None
    with sdk.resume():
        ...

Scope priority (lowest → highest — never change this order):
  1. Global  ~/.claude/
  2. App     ~/.cybersecsuite/
  3. Project $(pwd)/.claude/
  4. Session $(pwd)/.<scope>/sessions/<name>/  ← always wins for writes
"""
from __future__ import annotations

import contextlib
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Literal

from cybersecsuite._context import get_context
from cybersecsuite._session_io import (
    new_session_id,
    read_last_session,
    read_manifest,
    update_latest_symlink,
    write_last_session,
    write_manifest,
)
from template_engine.session_scope import (
    legacy_project_sessions_dir,
    project_session_scope_dir,
    project_sessions_dir,
    resolve_session_scope_name,
)
from template_engine.renderer import render as _render, render_string as _render_string

logger = logging.getLogger(__name__)

_POV = Literal["blue", "red", "purple", "hunter"]
_SCOPE = Literal["global", "app", "project", "session"]


class NoLastSessionError(RuntimeError):
    """Raised when sdk.resume() is called but no .last_session pointer exists."""


@dataclass
class SessionInfo:
    name: str
    path: str
    suspended_at: str


class CyberSecSuiteSDK:
    """Scope and session manager for CyberSecSuite."""

    def __init__(
        self,
        project_dir: Path | None = None,
        global_dir: Path | None = None,
        app_dir: Path | None = None,
        session_scope_name: str | None = None,
    ) -> None:
        self.project_dir: Path = project_dir or Path.cwd()
        self.global_dir: Path = global_dir or Path("~/.claude").expanduser()
        self.app_dir: Path = app_dir or Path("~/.cybersecsuite").expanduser()

        self._session_scope_name = resolve_session_scope_name(session_scope_name)
        self._session_scope_dir = project_session_scope_dir(self.project_dir, self._session_scope_name)
        self._sessions_dir: Path = project_sessions_dir(self.project_dir, self._session_scope_name)
        self._legacy_sessions_dir: Path = legacy_project_sessions_dir(self.project_dir)
        self._active_session: str | None = None
        self._session_id: str | None = None
        self._context_overlay: dict[str, Any] = {}
        self._scope: _SCOPE = "project"

    # ── Session dir helpers ───────────────────────────────────────────────────

    @property
    def _session_dir(self) -> Path | None:
        if self._active_session:
            return self._sessions_dir / self._active_session
        return None

    # ── Context ───────────────────────────────────────────────────────────────

    def context(self, session_id: str | None = None) -> dict[str, Any]:
        """Return merged context across all 4 scopes plus any in-memory overlay."""
        return get_context(
            project_dir=self.project_dir,
            session_id=session_id or self._active_session,
            extra=self._context_overlay,
        )

    def scope_paths(self) -> dict[str, Path]:
        return {
            "global": self.global_dir,
            "app": self.app_dir,
            "project": self.project_dir / ".claude",
            "session_scope": self._session_scope_dir,
            "session": self._session_dir or self._sessions_dir / "latest",
        }

    # ── Writers ───────────────────────────────────────────────────────────────

    def set(self, key: str, value: Any) -> None:
        """Set a context key in-memory (and persist to active session if open)."""
        self._context_overlay[key] = value
        self._persist_context_key(key, value)

    def set_pov(self, pov: _POV) -> None:
        self.set("pov", pov)

    def set_mitre_tactic(self, tactic: str) -> None:
        self.set("mitre_tactic", tactic)

    def set_linux_component(self, name: str) -> None:
        self.set("linux_component_name", name)

    def set_scope(self, scope: _SCOPE) -> None:
        """Change the read-priority anchor (writes still go to session if open)."""
        self._scope = scope

    def _persist_context_key(self, key: str, value: Any) -> None:
        """Write a single key to the active session's context.yaml."""
        if not self._session_dir:
            return
        import yaml  # pyyaml — runtime only
        ctx_path = self._session_dir / "context.yaml"
        existing: dict = {}
        if ctx_path.exists():
            try:
                existing = yaml.safe_load(ctx_path.read_text()) or {}
            except Exception:
                pass
        existing[key] = value
        self._session_dir.mkdir(parents=True, exist_ok=True)
        ctx_path.write_text(yaml.dump(existing, default_flow_style=False), encoding="utf-8")

    # ── Template rendering ────────────────────────────────────────────────────

    def render(self, template_name: str, **extra: Any) -> str:
        """Render a named template with the merged context + extras."""
        ctx = self.context()
        ctx.update(extra)
        return _render(
            template_name,
            ctx,
            project_dir=self.project_dir,
            session_id=self._active_session,
        )

    def render_string(self, source: str, **extra: Any) -> str:
        """Render an inline Jinja2 string with the merged context + extras."""
        ctx = self.context()
        ctx.update(extra)
        return _render_string(
            source,
            ctx,
            project_dir=self.project_dir,
            session_id=self._active_session,
        )

    # ── Session context manager ───────────────────────────────────────────────

    @contextlib.contextmanager
    def session(self, name: str) -> Generator[None, None, None]:
        """Open (or resume) a named session.

        On __enter__: creates dir, updates 'latest' symlink, restores manifest if resuming.
        On __exit__:  writes manifest (status=suspended), updates .last_session pointer.
        """
        session_dir = self._sessions_dir / name
        legacy_session_dir = self._legacy_sessions_dir / name
        session_dir.mkdir(parents=True, exist_ok=True)

        # Migrate minimal state from legacy .claude/sessions/<name> on first use.
        if legacy_session_dir.exists():
            legacy_manifest = read_manifest(legacy_session_dir)
            if legacy_manifest and not (session_dir / "session-manifest.json").exists():
                write_manifest(session_dir, legacy_manifest)
            legacy_ctx = legacy_session_dir / "context.yaml"
            if legacy_ctx.exists() and not (session_dir / "context.yaml").exists():
                shutil.copy2(legacy_ctx, session_dir / "context.yaml")
            legacy_tpl = legacy_session_dir / "templates"
            if legacy_tpl.exists() and not (session_dir / "templates").exists():
                shutil.copytree(legacy_tpl, session_dir / "templates", dirs_exist_ok=True)

        # Restore context from manifest if resuming
        existing = read_manifest(session_dir)
        if existing.get("context_snapshot"):
            restored = {k: v for k, v in existing["context_snapshot"].items()
                        if k not in self._context_overlay}
            self._context_overlay.update(restored)
            logger.info("sdk.session: resumed %r, restored %d context keys", name, len(restored))

        # Activate
        self._active_session = name
        self._session_id = existing.get("session_id") or new_session_id()
        start_time = existing.get("start_time") or datetime.now(timezone.utc).isoformat()

        update_latest_symlink(self._sessions_dir, session_dir)

        write_manifest(session_dir, {
            "name": name,
            "session_id": self._session_id,
            "status": "resuming" if existing else "active",
            "start_time": start_time,
            "end_time": None,
        })

        try:
            write_manifest(session_dir, {
                "name": name,
                "session_id": self._session_id,
                "status": "active",
                "start_time": start_time,
                "end_time": None,
            })
            yield
        finally:
            end_time = datetime.now(timezone.utc).isoformat()
            write_manifest(session_dir, {
                "name": name,
                "session_id": self._session_id,
                "status": "suspended",
                "start_time": start_time,
                "end_time": end_time,
                "context_snapshot": dict(self._context_overlay),
            })
            write_last_session(self._sessions_dir, name, session_dir)
            self._active_session = None
            self._session_id = None

    # ── Resume ────────────────────────────────────────────────────────────────

    def last_session(self) -> SessionInfo | None:
        """Return info about the last suspended session, or None."""
        data = read_last_session(self._sessions_dir)
        if not data:
            data = read_last_session(self._legacy_sessions_dir)
        if not data:
            return None
        return SessionInfo(
            name=data["name"],
            path=data["path"],
            suspended_at=data.get("suspended_at", ""),
        )

    @contextlib.contextmanager
    def resume(self) -> Generator[None, None, None]:
        """Resume the last suspended session.

        Raises NoLastSessionError if no .last_session pointer exists.
        """
        info = self.last_session()
        if not info:
            raise NoLastSessionError(
                "No last session found. Start a session first with sdk.session(name=...)."
            )
        with self.session(name=info.name):
            yield
