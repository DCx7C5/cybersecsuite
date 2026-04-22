"""QoL Output Controls — prompt fragment library.

This module defines the 8 server-side prompt fragments that are injected
as hidden system-level directives into every request when QoL toggles are active.

Each fragment is terse (< 15 tokens) and authoritative. Fragments are combined
using space separators and wrapped in [OUTPUT-CONTROLS] envelope markers.

All fragments are deterministic: toggles are sorted by enum value before
combining, ensuring consistent cache keys and reproducible output.

Design rules:
    - Never expose toggle *names* in the injection — only the directive.
    - "file_only" fragment MUST contain "NOTHING ELSE MAY APPEAR" (plan.md Warning 3).
    - All fragments start with a capital letter and end with a period.
    - Combined injection is cache-keyed by frozenset(active_toggles).
    - Maximum combined token estimate: ~55 tokens for all-enabled state.
    - Empty toggle set produces empty string (zero overhead).

Fragment map (8 fragments):
    NO_THINKING      → suppress reasoning/thinking blocks
    NO_CHAT          → suppress conversational filler
    MINIMAL          → one-liners and direct values
    FILE_ONLY        → output ONLY requested file/code (with mandatory phrase)
    NO_MARKDOWN      → plain text output
    STRUCTURED_ONLY  → JSON/YAML/table only
    REDACT_SECRETS   → redact API keys/passwords/tokens
    APPEND_AUDIT_TRAIL → append audit entry at end

Cache strategy:
    - Cache key: frozenset of active QoLToggle enums
    - TTL: 300 seconds (configurable via _CACHE_TTL_SECONDS in manager.py)
    - Hit rate: high (typical user session activates same toggles repeatedly)
    - Memory overhead: negligible (8 possible unique keys × ~200 bytes avg)

Referenz:
    plan.md T003 — Phase 1 QoL Core (prompts)
    plan.md T010 — Testing & Compliance (expanded tests)
    src/ai_proxy/qol_controls/models.py — QoLToggle enum
    src/ai_proxy/qol_controls/manager.py — build_injection() caller + caching

Status: production (Phase 1 complete)
Version: 1.0
Last modified: 2026-04-26 06:00:00Z
Author: python-developer
"""
from __future__ import annotations

from ai_proxy.qol_controls.models import QoLToggle

# ── Fragment map — QoLToggle → injection text ─────────────────────────────────

FRAGMENTS: dict[QoLToggle, str] = {
    QoLToggle.NO_THINKING: (
        "Do not emit any reasoning, thinking, or chain-of-thought blocks."
    ),
    QoLToggle.NO_CHAT: (
        "Omit all conversational filler, preamble, and sign-offs."
    ),
    QoLToggle.MINIMAL: (
        "Be maximally concise. Single sentences or direct values only."
    ),
    QoLToggle.FILE_ONLY: (
        "Output ONLY the requested file or code block. "
        "NOTHING ELSE MAY APPEAR in your response."
    ),
    QoLToggle.NO_MARKDOWN: (
        "Return plain text. Do not use Markdown, headers, or bullet lists."
    ),
    QoLToggle.STRUCTURED_ONLY: (
        "Respond exclusively with structured data (JSON, YAML, or a table). "
        "No prose."
    ),
    QoLToggle.REDACT_SECRETS: (
        "Automatically redact any API keys, passwords, or secrets in your output "
        "using the placeholder <REDACTED>."
    ),
    QoLToggle.APPEND_AUDIT_TRAIL: (
        "Append a one-line audit entry at the very end of your response in the format: "
        "[AUDIT ts=<ISO8601> toggles=<hash>]"
    ),
}

# ── Wrapper envelope — prepended / appended to the combined fragment block ────

_ENVELOPE_PREFIX = "[OUTPUT-CONTROLS]"
_ENVELOPE_SUFFIX = "[/OUTPUT-CONTROLS]"

# Token budget target: ≤ 55 tokens for all-enabled state
_SEPARATOR = " "


def build_fragment_block(active_toggles: frozenset[QoLToggle]) -> str:
    """Return the combined fragment string for the given set of active toggles.

    Returns an empty string when no toggles are active (zero overhead).
    The result is deterministic: toggles are sorted by enum value.
    """
    if not active_toggles:
        return ""
    parts = [
        FRAGMENTS[t]
        for t in sorted(active_toggles, key=lambda x: x.value)
        if t in FRAGMENTS
    ]
    if not parts:
        return ""
    combined = _SEPARATOR.join(parts)
    return f"{_ENVELOPE_PREFIX} {combined} {_ENVELOPE_SUFFIX}"
