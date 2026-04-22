"""QoL Output Controls — Pydantic v2 models.

QoLToggle   — individual boolean switch (8 values)
QoLSettings — aggregated per-scope configuration persisted to ~/.cybersecsuite/data/qol.json

Storage layout (JSON, no DB):
    {base_dir}/qol.json  — active settings per scope
    {base_dir}/qol_presets.json  — named preset bundles

This module defines the core data structures for QoL (Quality of Life) output
control toggles. All toggles are mutually independent except for the
dangerous combinations defined in _DANGEROUS_COMBOS.

Referenz:
    plan.md T002 — Phase 1 QoL Core
    plan.md T010 — Testing & Compliance (expanded tests)
    src/csmcp/cybersec/helpers.py — scope helpers reused here
    src/ai_proxy/qol_controls/manager.py — QoLManager (consumer)
    src/ai_proxy/qol_controls/prompts.py — fragment definitions

Toggles (8 total):
    1. no_thinking — suppress reasoning/thinking blocks
    2. no_chat — suppress conversational filler
    3. minimal — one-liners and direct answers only
    4. file_only — output only code/files, NOTHING ELSE MAY APPEAR
    5. no_markdown — plain text, no Markdown
    6. structured_only — JSON/YAML/table only, no prose
    7. redact_secrets — auto-redact API keys, passwords, tokens
    8. append_audit_trail — append audit entry to response

Dangerous combinations (validated by validate_toggle_combo):
    - file_only + append_audit_trail (contradictory: file vs append)
    - file_only + structured_only (contradictory: file vs structured)
    - minimal + append_audit_trail (contradictory: minimal vs append)

Status: production (Phase 1 complete, Phase 1B observability in progress)
Version: 1.0
Last modified: 2026-04-26 06:00:00Z
Author: python-developer
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class QoLToggle(str, Enum):
    """All supported QoL output-control toggles."""

    # ── Output suppression ──────────────────────────────────────────────────
    NO_THINKING = "no_thinking"
    """Suppress any <thinking> / reasoning blocks from LLM output."""

    NO_CHAT = "no_chat"
    """Suppress conversational filler. Return only the requested artefact."""

    MINIMAL = "minimal"
    """Absolute minimum output — one-liners and direct answers only."""

    FILE_ONLY = "file_only"
    """Only produce file/code output; NOTHING ELSE MAY APPEAR in the response."""

    # ── Format controls ─────────────────────────────────────────────────────
    NO_MARKDOWN = "no_markdown"
    """Return plain text; do not use Markdown formatting."""

    STRUCTURED_ONLY = "structured_only"
    """Output only structured data (JSON / YAML / table). No prose."""

    # ── Safety / audit ──────────────────────────────────────────────────────
    REDACT_SECRETS = "redact_secrets"
    """Auto-redact any API keys, passwords, or tokens that appear in output."""

    APPEND_AUDIT_TRAIL = "append_audit_trail"
    """Append a compact audit trail (timestamp + model + toggle hash) to every response."""


_TOGGLE_DESCRIPTIONS: dict[QoLToggle, str] = {
    QoLToggle.NO_THINKING: "Suppress reasoning/thinking blocks",
    QoLToggle.NO_CHAT: "Suppress conversational filler",
    QoLToggle.MINIMAL: "Absolute minimum output",
    QoLToggle.FILE_ONLY: "File/code output only — NOTHING ELSE MAY APPEAR",
    QoLToggle.NO_MARKDOWN: "Plain text, no Markdown",
    QoLToggle.STRUCTURED_ONLY: "Structured data output only (JSON/YAML/table)",
    QoLToggle.REDACT_SECRETS: "Auto-redact secrets in output",
    QoLToggle.APPEND_AUDIT_TRAIL: "Append audit trail to each response",
}


def toggle_description(t: QoLToggle) -> str:
    return _TOGGLE_DESCRIPTIONS.get(t, t.value)


# ── Dangerous toggle combinations ─────────────────────────────────────────────

class QoLSecurityError(ValueError):
    """Raised when an invalid/dangerous QoL toggle combination is requested."""


# Pairs that produce contradictory directives and should never coexist.
_DANGEROUS_COMBOS: tuple[frozenset[QoLToggle], ...] = (
    frozenset({QoLToggle.FILE_ONLY, QoLToggle.APPEND_AUDIT_TRAIL}),   # file-only but append text
    frozenset({QoLToggle.FILE_ONLY, QoLToggle.STRUCTURED_ONLY}),      # file-only vs structured-data-only
    frozenset({QoLToggle.MINIMAL, QoLToggle.APPEND_AUDIT_TRAIL}),     # minimal but append audit text
)


def validate_toggle_combo(toggles: frozenset["QoLToggle"]) -> None:
    """Raise QoLSecurityError if *toggles* contains a contradictory combination."""
    for bad_pair in _DANGEROUS_COMBOS:
        if bad_pair.issubset(toggles):
            names = ", ".join(sorted(t.value for t in bad_pair))
            raise QoLSecurityError(
                f"Contradictory QoL toggle combination: [{names}]. "
                "These directives cannot coexist — disable one before enabling the other."
            )


class QoLSettings(BaseModel):
    """Active QoL configuration for a scope / session.

    Fields
    ------
    enabled_toggles : set of active QoLToggle values
    scope           : the scope this setting applies to (project / session / global)
    preset_name     : optional label if loaded from a named preset
    """

    model_config = {"frozen": False, "extra": "ignore"}

    enabled_toggles: set[QoLToggle] = Field(default_factory=set)
    scope: str = Field(default="session")
    preset_name: str | None = Field(default=None)

    # ── Convenience helpers ─────────────────────────────────────────────────

    def is_active(self, toggle: QoLToggle | str) -> bool:
        t = QoLToggle(toggle) if isinstance(toggle, str) else toggle
        return t in self.enabled_toggles

    def activate(self, *toggles: QoLToggle | str) -> "QoLSettings":
        for t in toggles:
            self.enabled_toggles.add(QoLToggle(t) if isinstance(t, str) else t)
        return self

    def deactivate(self, *toggles: QoLToggle | str) -> "QoLSettings":
        for t in toggles:
            self.enabled_toggles.discard(QoLToggle(t) if isinstance(t, str) else t)
        return self

    def as_dict(self) -> dict[str, Any]:
        return {
            "enabled_toggles": [t.value for t in sorted(self.enabled_toggles, key=lambda x: x.value)],
            "scope": self.scope,
            "preset_name": self.preset_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QoLSettings":
        raw_toggles = data.get("enabled_toggles", [])
        toggles: set[QoLToggle] = set()
        for v in raw_toggles:
            try:
                toggles.add(QoLToggle(v))
            except ValueError:
                pass  # ignore unknown / removed toggles gracefully
        return cls(
            enabled_toggles=toggles,
            scope=data.get("scope", "session"),
            preset_name=data.get("preset_name"),
        )


# ── Named presets ─────────────────────────────────────────────────────────────

BUILTIN_PRESETS: dict[str, QoLSettings] = {
    "silent": QoLSettings(
        enabled_toggles={QoLToggle.NO_THINKING, QoLToggle.NO_CHAT, QoLToggle.MINIMAL},
        preset_name="silent",
    ),
    "code-only": QoLSettings(
        enabled_toggles={QoLToggle.FILE_ONLY, QoLToggle.NO_THINKING, QoLToggle.NO_CHAT},
        preset_name="code-only",
    ),
    "structured": QoLSettings(
        enabled_toggles={QoLToggle.STRUCTURED_ONLY, QoLToggle.NO_THINKING},
        preset_name="structured",
    ),
    "audit": QoLSettings(
        enabled_toggles={QoLToggle.APPEND_AUDIT_TRAIL, QoLToggle.REDACT_SECRETS},
        preset_name="audit",
    ),
    "plain-text": QoLSettings(
        enabled_toggles={QoLToggle.NO_MARKDOWN, QoLToggle.NO_THINKING},
        preset_name="plain-text",
    ),
}
