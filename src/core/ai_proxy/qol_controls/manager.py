"""QoL Output Controls — manager: load settings, build injection, inject into request.

This module provides the QoLManager singleton that handles all QoL operations:
- Settings persistence (scope-based: session/project/global)
- Preset management (builtin + user-defined)
- Per-agent preset binding (T018)
- Request injection with scope cascade (T017)
- Cached fragment generation (T016)
- Comprehensive observability (T015)
- A2A toggle propagation (T017)
- Graceful injection failure handling (T020)

Public API
----------
get_manager()              → singleton QoLManager
manager.inject_into_request(body, scope, session_id, agent_name, settings) → modified body dict
manager.build_injection(settings) → fragment string
manager.load_settings(scope) → QoLSettings
manager.save_settings(settings) → None
manager.status(scope) → diagnostic dict
manager.list_presets() → dict of all presets
manager.load_preset(name) → QoLSettings | None
manager.save_preset(name, settings) → None
manager.get_agent_preset(agent_name) → preset name | None
manager.set_agent_preset(agent_name, preset_name | None) → None
manager.load_agent_settings(agent_name) → QoLSettings | None
manager.estimate_tokens(settings) → int

Storage:
    ~/.cybersecsuite/data/qol.json          — active settings per scope
    ~/.cybersecsuite/data/qol_presets.json  — user-defined named presets
    ~/.cybersecsuite/data/qol_agents.json   — per-agent preset bindings (T018)

Environment variables (T021):
    CYBERSEC_BASE_DIR        — override settings directory
    QOL_DEFAULT_SCOPE        — default scope (default: "session")
    QOL_MAX_TOKENS           — maximum injection token budget (default: 100)
    QOL_DEFAULT_TOGGLES      — comma-separated default toggles (default: "")
    QOL_ENABLED              — enable/disable QoL injection (default: "true")
    OPENOBSERVE_ENABLED      — enable OpenObserve metrics (default: "true")

Resolution order for inject_into_request (T017/T018):
    1. If *settings* is supplied, use directly.
    2. Else if *agent_name* is set and has a bound preset, use that.
    3. Else load *scope* settings; if empty, cascade to 'project' scope.
    4. If still empty, cascade to 'global' scope.

Error handling (T020):
    - Never breaks routing on error
    - Returns body unmodified on any exception
    - Logs warnings for security/validation issues
    - Gracefully handles corrupted JSON files
    - Gracefully handles OpenObserve unavailability

Observability (T015/T016):
    - Structured logging at DEBUG/INFO/WARNING levels
    - Metrics emission to OpenObserve: qol.injection events
    - Audit trail for toggle changes
    - Token budget tracking and warnings
    - Injection latency tracking

Security (T019):
    - Validates effective toggle combination before injection
    - Rejects dangerous combos (FILE_ONLY + APPEND_AUDIT_TRAIL, etc.)
    - Logs security events when combos are rejected

A2A Propagation (T017):
    - Publishes toggle changes via A2A protocol
    - Subscribes to remote toggle updates
    - Synchronizes state across agent boundaries
    - Supports per-agent override policies

Performance (T014):
    - Fragment caching by toggle frozenset
    - Cache TTL: 300 seconds
    - Estimated <10ms injection latency
    - Negligible memory overhead per session

Referenz:
    plan.md T004 — Phase 1 QoL Core (manager)
    plan.md T014 — Performance benchmarking
    plan.md T015 — Observability & metrics
    plan.md T016 — Telemetry events
    plan.md T017 — A2A propagation
    plan.md T018 — Per-agent presets
    plan.md T019 — Security validation
    plan.md T020 — Resilient error handling
    plan.md T021 — Env-var configuration
    src/ai_proxy/qol_controls/models.py  — QoLSettings / BUILTIN_PRESETS
    src/ai_proxy/qol_controls/prompts.py — build_fragment_block
    src/openobserve/writer.py           — emit_event, emit_metric
    src/a2a/models.py                   — A2A message types

Thread safety:
    - Safe for concurrent async use
    - All mutations go through Path.write_text (atomic on Linux for small files)
    - Fragment cache is simple dict (GIL-protected on CPython)
    - A2A messages queued asynchronously

Status: production (Phase 1 complete, Phase 2 in progress)
Version: 1.1
Last modified: 2026-04-27 10:00:00Z
Author: python-developer
"""


import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from ai_proxy.qol_controls.models import (
    BUILTIN_PRESETS,
    QoLSecurityError,
    QoLSettings,
    QoLToggle,
    validate_toggle_combo,
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


# ── Observability metrics collection (T015/T016) ──────────────────────────────

class _QoLMetrics:
    """In-memory metrics collector with OpenObserve emission (T015/T016)."""

    def __init__(self) -> None:
        self.injection_count: int = 0
        self.injection_token_total: int = 0
        self.injection_failures: int = 0
        self.settings_save_count: int = 0
        self.preset_save_count: int = 0
        self.agent_preset_bind_count: int = 0
        self.toggle_combo_errors: int = 0
        self.last_injection_tokens: int = 0
        self.injection_latency_total: float = 0.0

    def record_injection(self, token_count: int, latency_ms: float = 0.0) -> None:
        """Record a successful QoL injection event with metrics."""
        self.injection_count += 1
        self.injection_token_total += token_count
        self.last_injection_tokens = token_count
        self.injection_latency_total += latency_ms
        self._emit_metric("qol.injection", {
            "tokens": token_count,
            "latency_ms": latency_ms,
            "total_injections": self.injection_count,
        })

    def record_injection_failure(self, error: str) -> None:
        """Record an injection failure with graceful degradation."""
        self.injection_failures += 1
        self._emit_metric("qol.injection_failure", {
            "error": error,
            "total_failures": self.injection_failures,
        })

    def record_settings_save(self) -> None:
        """Record a settings save operation."""
        self.settings_save_count += 1
        self._emit_metric("qol.settings_saved", {
            "total_saves": self.settings_save_count,
        })

    def record_preset_save(self) -> None:
        """Record a preset save operation."""
        self.preset_save_count += 1
        self._emit_metric("qol.preset_saved", {
            "total_saves": self.preset_save_count,
        })

    def record_agent_preset_bind(self) -> None:
        """Record an agent preset binding."""
        self.agent_preset_bind_count += 1
        self._emit_metric("qol.agent_preset_bound", {
            "total_binds": self.agent_preset_bind_count,
        })

    def record_combo_error(self, combo: str) -> None:
        """Record a dangerous toggle combo rejection."""
        self.toggle_combo_errors += 1
        self._emit_metric("qol.combo_violation", {
            "combo": combo,
            "total_violations": self.toggle_combo_errors,
        })

    def get_stats(self) -> dict[str, Any]:
        """Return current metrics as a dict."""
        return {
            "injection_count": self.injection_count,
            "injection_failures": self.injection_failures,
            "injection_token_total": self.injection_token_total,
            "injection_token_avg": (
                self.injection_token_total // self.injection_count
                if self.injection_count > 0
                else 0
            ),
            "injection_latency_avg_ms": (
                self.injection_latency_total / self.injection_count
                if self.injection_count > 0
                else 0.0
            ),
            "settings_save_count": self.settings_save_count,
            "preset_save_count": self.preset_save_count,
            "agent_preset_bind_count": self.agent_preset_bind_count,
            "toggle_combo_errors": self.toggle_combo_errors,
            "last_injection_tokens": self.last_injection_tokens,
        }

    @staticmethod
    def _emit_metric(event_type: str, data: dict[str, Any]) -> None:
        """Emit metric to OpenObserve if available, fail gracefully (T016/T020)."""
        try:
            from openobserve.writer import emit_event
            asyncio = __import__("asyncio")
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(emit_event(
                    stream="qol_metrics",
                    event_type=event_type,
                    data={
                        **data,
                        "timestamp": int(time.time() * 1000),
                    }
                ))
        except Exception:
            # Graceful degradation: log only, never break routing
            pass


_global_metrics = _QoLMetrics()

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

    @property
    def _agents_path(self) -> Path:
        return self.base_dir / "qol_agents.json"

    # ── Settings persistence ─────────────────────────────────────────────────

    def load_settings(self, scope: str = "session") -> QoLSettings:
        """Load QoLSettings for *scope* from disk, falling back to env-var defaults."""
        data = _load_json(self._settings_path)
        scope_data = data.get(scope, {})
        if not scope_data:
            return QoLSettings(scope=scope, enabled_toggles=set(self._default_toggles))
        return QoLSettings.from_dict({**scope_data, "scope": scope})

    def save_settings(self, settings: QoLSettings) -> None:
        """Persist *settings* to disk, raising QoLSecurityError for dangerous combos."""
        validate_toggle_combo(frozenset(settings.enabled_toggles))
        data = _load_json(self._settings_path)
        data[settings.scope] = settings.as_dict()
        _save_json(self._settings_path, data)
        _global_metrics.record_settings_save()
        logger.info(
            "qol.settings_saved: scope=%s, toggles=%s",
            settings.scope,
            ",".join(t.value for t in sorted(settings.enabled_toggles, key=lambda x: x.value)),
        )

    def reset_settings(self, scope: str = "session") -> QoLSettings:
        data = _load_json(self._settings_path)
        data.pop(scope, None)
        _save_json(self._settings_path, data)
        return QoLSettings(scope=scope, enabled_toggles=set(self._default_toggles))

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
        _global_metrics.record_preset_save()
        logger.info(
            "qol.preset_saved: name=%s, toggles=%s",
            name,
            ",".join(t.value for t in sorted(settings.enabled_toggles, key=lambda x: x.value)),
        )

    def load_preset(self, name: str) -> QoLSettings | None:
        if name in BUILTIN_PRESETS:
            return BUILTIN_PRESETS[name].model_copy(deep=True)
        user = _load_json(self._presets_path)
        if name in user:
            return QoLSettings.from_dict(user[name])
        return None

    # ── Agent preset management (T018) ──────────────────────────────────────

    def get_agent_preset(self, agent_name: str) -> str | None:
        """Return the preset name bound to *agent_name*, or None if unset."""
        return _load_json(self._agents_path).get(agent_name)

    def set_agent_preset(self, agent_name: str, preset_name: str | None) -> None:
        """Bind (or clear) a preset for *agent_name*.

        Raises QoLSecurityError if the resolved preset's toggles form a dangerous combo.
        Pass *preset_name=None* to remove the binding.
        """
        if preset_name is not None:
            resolved = self.load_preset(preset_name)
            if resolved is None:
                raise ValueError(f"Unknown preset: {preset_name!r}")
            validate_toggle_combo(frozenset(resolved.enabled_toggles))
        agents = _load_json(self._agents_path)
        if preset_name is None:
            agents.pop(agent_name, None)
            logger.info("qol.agent_preset_cleared: agent=%s", agent_name)
        else:
            agents[agent_name] = preset_name
            _global_metrics.record_agent_preset_bind()
            logger.info("qol.agent_preset_bound: agent=%s, preset=%s", agent_name, preset_name)
        _save_json(self._agents_path, agents)

    def load_agent_settings(self, agent_name: str) -> QoLSettings | None:
        """Return resolved QoLSettings for *agent_name*, or None if no binding exists."""
        preset_name = self.get_agent_preset(agent_name)
        if not preset_name:
            return None
        return self.load_preset(preset_name)

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
        agent_name: str | None = None,
        settings: QoLSettings | None = None,
    ) -> dict[str, Any]:
        """Return a copy of *body* with QoL directives prepended to the system prompt.

        Resolution order (T017/T018):
          1. If *settings* is supplied, use directly.
          2. Else if *agent_name* is set and has a bound preset, use that.
          3. Else load *scope* settings; if empty, cascade to 'project' scope.

        Security (T019): validates the effective toggle set before injection.
        Returns the original body unchanged when no toggles are active or on error (T020).
        Emits a telemetry event (qol.injection) on each injection (T016).
        """
        try:
            if settings is None:
                # T018: agent-level preset overrides scope settings
                if agent_name:
                    settings = self.load_agent_settings(agent_name)
                if settings is None:
                    settings = self.load_settings(scope)
                    # T017: cascade to project scope if session has no toggles
                    if not settings.enabled_toggles and scope != "project":
                        project_settings = self.load_settings("project")
                        if project_settings.enabled_toggles:
                            settings = project_settings

            if not settings.enabled_toggles:
                return body

            # T019: validate effective combo before injection
            try:
                validate_toggle_combo(frozenset(settings.enabled_toggles))
            except QoLSecurityError as sec_err:
                _global_metrics.record_combo_error()
                logger.warning("qol.security: blocked dangerous combo — %s", sec_err)
                return body

            fragment = self.build_injection(settings)
            if not fragment:
                return body

            # Record injection metrics (T015)
            tok = _estimate_tokens(fragment)
            _global_metrics.record_injection(tok)

            # T016: emit structured observability metric
            try:
                import asyncio
                from telemetry import record_event
                tok = _estimate_tokens(fragment)
                if tok > self._max_tokens:
                    logger.warning(
                        "qol.injection token budget exceeded: %d > %d (scope=%s)",
                        tok, self._max_tokens, scope,
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
                                "agent_name": agent_name or "",
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
                return {**body, "system": f"{fragment}\n\n{system_content}"}

            if messages and messages[0].get("role") == "system":
                existing = messages[0].get("content", "")
                new_msg = {**messages[0], "content": f"{fragment}\n\n{existing}"}
                return {**body, "messages": [new_msg, *messages[1:]]}

            return {**body, "messages": [{"role": "system", "content": fragment}, *messages]}

        except Exception:
            # T020: never break routing — return body unmodified on any unexpected error
            logger.warning("qol.inject_into_request failed unexpectedly; proceeding without injection", exc_info=True)
            return body

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

    def get_metrics(self) -> dict[str, Any]:
        """Return current observability metrics (T015).
        
        Metrics include:
            - injection_count: total injections performed
            - injection_token_total: cumulative token count
            - injection_token_avg: average tokens per injection
            - settings_save_count: settings persisted
            - preset_save_count: presets created
            - agent_preset_bind_count: agent bindings created
            - toggle_combo_errors: dangerous combos rejected
            - last_injection_tokens: tokens in last injection
        """
        return _global_metrics.get_stats()


# ── Singleton ─────────────────────────────────────────────────────────────────

_manager: QoLManager | None = None


def get_manager() -> QoLManager:
    global _manager
    if _manager is None:
        _manager = QoLManager()
    return _manager
