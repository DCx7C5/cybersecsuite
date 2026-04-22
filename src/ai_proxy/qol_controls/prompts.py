"""QoL Output Controls — prompt fragment library.

8 strong server-side fragments injected as a hidden system-level directive.
All fragments must be terse (< 15 tokens each) and authoritative.

Design rules:
    - Never expose toggle *names* in the injection — only the directive.
    - "file_only" fragment MUST contain "NOTHING ELSE MAY APPEAR" (plan.md Warning 3).
    - All fragments start with a capital letter and end with a period.
    - Combined injection is cache-keyed by frozenset(active_toggles).

Referenz:
    plan.md T003 — Phase 1 QoL Core
    src/ai_proxy/qol_controls/models.py — QoLToggle enum
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
