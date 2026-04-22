"""QoL Output Controls — manager: load settings, build injection, inject into request.

Public API
----------
get_manager()              → singleton QoLManager
manager.inject_into_request(body, scope, session_id) → modified body dict

Storage:
    ~/.cybersecsuite/data/qol.json          — active settings per scope
    ~/.cybersecsuite/data/qol_presets.json  — user-defined named presets

Referenz:
    plan.md T004 — Phase 1 QoL Core
    src/ai_proxy/qol_controls/models.py  — QoLSettings / BUILTIN_PRESETS
    src/ai_proxy/qol_controls/prompts.py — build_fragment_block
    src/csmcp/cybersec/helpers.py        — _get_base_dir scope helpers
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from ai_proxy.qol_controls.models import (
    BUILTIN_PRESETS,
    QoLSettings,
    QoLToggle,
)
from ai_proxy.qol_controls.prompts import build_fragment_block

logger = logging.getLogger("ai_proxy.qol_controls")

_TOKEN_WARN_THRESHOLD = 100  # warn if injected system text exceeds this many tokens (est.)
_CACHE_TTL_SECONDS = 300


def _get_base_dir() -> Path:
    base = os.environ.get("CYBERSEC_BASE_DIR") or os.environ.get("MALWAREHUNTER_BASE_DIR")
    if base:
        return Path(base).expanduser().resolve()
    plugin = os.environ.get("PLUGIN_DATA_DIR") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if plugin:
        return Path(plugin).expanduser().resolve() / "cybersec"
    home = Path(os.environ.get("CYBERSECSUITE_HOME", str(Path.home() / ".cybersecsuite")))
    return home.expanduser().resolve() / "data"


def _load_json(path: Path) -> dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token (good enough for budget guard)."""
    return max(1, len(text) // 4)


def _toggle_hash(toggles: frozenset[QoLToggle]) -> str:
    key = ",".join(sorted(t.value for t in toggles))
    return hashlib.blake2b(key.encode(), digest_size=4).hexdigest()


class QoLManager:
    """Loads, persists, and applies QoL output-control settings.

    Thread-safe for concurrent async use (all mutations go through Path.write_text
    which is atomic on Linux for small files).
    """

    def __init__(self) -> None:
        self._base_dir: Path | None = None
        # Cache: frozenset[QoLToggle] → (fragment_str, timestamp)
        self._fragment_cache: dict[frozenset, tuple[str, float]] = {}

        # ── Env-var defaults (T021) ──────────────────────────────────────────
        self._default_scope: str = os.environ.get("QOL_DEFAULT_SCOPE", "session")
        self._max_tokens: int = int(os.environ.get("QOL_MAX_TOKENS", "100"))
        raw_defaults = os.environ.get("QOL_DEFAULT_TOGGLES", "")
        self._default_toggles: frozenset[QoLToggle] = frozenset(
            t
            for v in (s.strip() for s in raw_defaults.split(","))
            if v
            for t in [
                next(
                    (e for e in QoLToggle if e.value == v),
                    None,  # type: ignore[arg-type]
                )
            ]
            if t is not None
        )

    # ── Paths ────────────────────────────────────────────────────────────────

    @property
    def base_dir(self) -> Path | None:
        if self._base_dir is None:
            self._base_dir = _get_base_dir()
        return self._base_dir

    @property
    def _settings_path(self) -> Path:
        return self.base_dir / "qol.json"

    @property
    def _presets_path(self) -> Path:
        return self.base_dir / "qol_presets.json"

    # ── Settings persistence ─────────────────────────────────────────────────

    def load_settings(self, scope: str = "session") -> QoLSettings:
        """Load QoLSettings for *scope* from disk, falling back to env-var defaults."""
        data = _load_json(self._settings_path)
        scope_data = data.get(scope, {})
        if not scope_data:
            return QoLSettings(scope=scope, enabled_toggles=set(self._default_toggles))
        return QoLSettings.from_dict({**scope_data, "scope": scope})

    def save_settings(self, settings: QoLSettings) -> None:
        data = _load_json(self._settings_path)
        data[settings.scope] = settings.as_dict()
        _save_json(self._settings_path, data)

    def reset_settings(self, scope: str = "session") -> QoLSettings:
        data = _load_json(self._settings_path)
        data.pop(scope, None)
        _save_json(self._settings_path, data)
        return QoLSettings(scope=scope)

    # ── Preset management ────────────────────────────────────────────────────

    def list_presets(self) -> dict[str, dict[str, Any]]:
        """Return all available presets (builtin + user-defined)."""
        result: dict[str, dict[str, Any]] = {}
        for name, s in BUILTIN_PRESETS.items():
            result[name] = {**s.as_dict(), "source": "builtin"}
        user = _load_json(self._presets_path)
        for name, raw in user.items():
            result[name] = {**raw, "source": "user"}
        return result

    def save_preset(self, name: str, settings: QoLSettings) -> None:
        user = _load_json(self._presets_path)
        user[name] = settings.as_dict()
        _save_json(self._presets_path, user)

    def load_preset(self, name: str) -> QoLSettings | None:
        if name in BUILTIN_PRESETS:
            return BUILTIN_PRESETS[name].model_copy(deep=True)
        user = _load_json(self._presets_path)
        if name in user:
            return QoLSettings.from_dict(user[name])
        return None

    # ── Injection ────────────────────────────────────────────────────────────

    def build_injection(self, settings: QoLSettings) -> str:
        """Build the prompt fragment string for *settings*.

        Result is cached by toggle frozenset with TTL to avoid repeated work.
        """
        key = frozenset(settings.enabled_toggles)
        cached = self._fragment_cache.get(key)
        if cached:
            fragment, ts = cached
            if time.monotonic() - ts < _CACHE_TTL_SECONDS:
                return fragment

        fragment = build_fragment_block(key)
        self._fragment_cache[key] = (fragment, time.monotonic())

        if fragment:
            tok = _estimate_tokens(fragment)
            if tok > _TOKEN_WARN_THRESHOLD:
                logger.warning(
                    "QoL injection is large: ~%d tokens (target ≤ %d). "
                    "Consider reducing active toggles.",
                    tok, _TOKEN_WARN_THRESHOLD,
                )
        return fragment

    def estimate_tokens(self, settings: QoLSettings) -> int:
        """Return estimated token count for the injection block."""
        return _estimate_tokens(self.build_injection(settings))

    def inject_into_request(
        self,
        body: dict[str, Any],
        scope: str = "session",
        session_id: str | None = None,
        settings: QoLSettings | None = None,
    ) -> dict[str, Any]:
        """Return a copy of *body* with QoL directives prepended to the system prompt.

        If *settings* is provided it is used directly; otherwise settings are loaded
        from disk for *scope* (enables per-request override without I/O for hot paths
        when the caller supplies pre-loaded settings).

        Returns the original body unchanged when no toggles are active.
        Emits a telemetry event (qol.injection) recording token count when injecting.
        """
        if settings is None:
            settings = self.load_settings(scope)

        if not settings.enabled_toggles:
            return body

        fragment = self.build_injection(settings)
        if not fragment:
            return body

        # Emit observability metric (fire-and-forget; never blocks routing)
        try:
            import asyncio
            from telemetry import record_event
            tok = _estimate_tokens(fragment)
            if tok > self._max_tokens:
                logger.warning(
                    "qol.injection token budget exceeded: %d > %d (scope=%s)",
                    tok,
                    self._max_tokens,
                    scope,
                )
            toggle_names = ",".join(sorted(t.value for t in settings.enabled_toggles))
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(
                    record_event(
                        "qol.injection",
                        float(tok),
                        labels={
                            "scope": scope,
                            "toggle_count": str(len(settings.enabled_toggles)),
                            "toggle_names": toggle_names,
                            "session_id": session_id or "",
                            "over_budget": str(tok > self._max_tokens).lower(),
                        },
                    )
                )
        except Exception:
            pass

        # Prepend to existing system message or insert a new one
        messages: list[dict[str, Any]] = list(body.get("messages", []))
        system_content = body.get("system", "")

        if system_content:
            # String system field (Anthropic-style)
            modified_system = f"{fragment}\n\n{system_content}"
            return {**body, "system": modified_system}

        if messages and messages[0].get("role") == "system":
            existing = messages[0].get("content", "")
            new_msg = {**messages[0], "content": f"{fragment}\n\n{existing}"}
            return {**body, "messages": [new_msg, *messages[1:]]}

        # No system message — insert one
        new_system = {"role": "system", "content": fragment}
        return {**body, "messages": [new_system, *messages]}

    # ── Diagnostics ──────────────────────────────────────────────────────────

    def status(self, scope: str = "session") -> dict[str, Any]:
        settings = self.load_settings(scope)
        fragment = self.build_injection(settings)
        return {
            "scope": scope,
            "active_toggles": [t.value for t in sorted(settings.enabled_toggles, key=lambda x: x.value)],
            "preset_name": settings.preset_name,
            "fragment_preview": fragment[:120] + ("…" if len(fragment) > 120 else ""),
            "estimated_tokens": _estimate_tokens(fragment) if fragment else 0,
            "toggle_hash": _toggle_hash(frozenset(settings.enabled_toggles)),
        }


# ── Singleton ─────────────────────────────────────────────────────────────────

_manager: QoLManager | None = None


def get_manager() -> QoLManager | None:
    global _manager
    if _manager is None:
        _manager = QoLManager()
    return _manager
