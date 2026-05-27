"""QoL Output Controls — msgspec.Struct models.

QoLToggle   — individual boolean switch
QoLSettings — aggregated per-scope configuration as immutable msgspec.Struct
"""

from enum import Enum
from collections.abc import Iterable, Mapping

import msgspec

from css.core.exceptions import BaseCoreException


class QoLToggle(str, Enum):
    """All supported QoL output-control toggles."""

    NO_THINKING = "no_thinking"
    NO_CHAT = "no_chat"
    MINIMAL = "minimal"
    FILE_ONLY = "file_only"
    NO_MARKDOWN = "no_markdown"
    STRUCTURED_ONLY = "structured_only"
    REDACT_SECRETS = "redact_secrets"
    APPEND_AUDIT_TRAIL = "append_audit_trail"


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

_QOL_TOGGLE_VALUES: set[str] = {toggle.value for toggle in QoLToggle}
_DANGEROUS_COMBOS: dict[frozenset[QoLToggle], str] = {
    frozenset({QoLToggle.FILE_ONLY, QoLToggle.APPEND_AUDIT_TRAIL}): (
        "file_only cannot be combined with append_audit_trail"
    ),
    frozenset({QoLToggle.FILE_ONLY, QoLToggle.STRUCTURED_ONLY}): (
        "file_only cannot be combined with structured_only"
    ),
    frozenset({QoLToggle.MINIMAL, QoLToggle.APPEND_AUDIT_TRAIL}): (
        "minimal cannot be combined with append_audit_trail"
    ),
}


class QoLSecurityError(BaseCoreException):
    """Raised when an unsafe QoL toggle combination is requested."""

    def __init__(self, combination: frozenset[QoLToggle], active: set[QoLToggle]):
        combo_values = tuple(sorted(toggle.value for toggle in combination))
        active_values = tuple(sorted(toggle.value for toggle in active))
        message = _DANGEROUS_COMBOS[combination]
        super().__init__(
            message,
            dir_name="settings",
            context={
                "error_code": "qol.dangerous_combo",
                "combination": combo_values,
                "active_toggles": active_values,
            },
        )
        self.combination = combo_values
        self.active_toggles = active_values


def _coerce_toggles(toggles: Iterable[QoLToggle | str]) -> set[QoLToggle]:
    normalized: set[QoLToggle] = set()
    for toggle in toggles:
        normalized.add(QoLToggle(toggle) if isinstance(toggle, str) else toggle)
    return normalized


def validate_toggle_combo(toggles: Iterable[QoLToggle | str]) -> None:
    """Validate active toggles and raise QoLSecurityError for forbidden sets."""
    normalized = _coerce_toggles(toggles)
    for dangerous_combo in _DANGEROUS_COMBOS:
        if dangerous_combo.issubset(normalized):
            raise QoLSecurityError(dangerous_combo, normalized)


def toggle_description(t: QoLToggle) -> str:
    """Return a human-readable description for *t*."""
    return _TOGGLE_DESCRIPTIONS.get(t, t.value)


class QoLSettings(msgspec.Struct, frozen=True, kw_only=True):
    """Active QoL configuration for a scope / session.

    Immutable — activate() / deactivate() return new instances.
    """

    enabled_toggles: set[QoLToggle] = msgspec.field(default_factory=set)
    scope: str = "session"
    preset_name: str | None = None

    def is_active(self, toggle: QoLToggle | str) -> bool:
        t = QoLToggle(toggle) if isinstance(toggle, str) else toggle
        return t in self.enabled_toggles

    def activate(self, *toggles: QoLToggle | str) -> QoLSettings:
        new_set = set(self.enabled_toggles)
        for t in toggles:
            new_set.add(QoLToggle(t) if isinstance(t, str) else t)
        return QoLSettings(enabled_toggles=new_set, scope=self.scope, preset_name=self.preset_name)

    def deactivate(self, *toggles: QoLToggle | str) -> QoLSettings:
        new_set = set(self.enabled_toggles)
        for t in toggles:
            new_set.discard(QoLToggle(t) if isinstance(t, str) else t)
        return QoLSettings(enabled_toggles=new_set, scope=self.scope, preset_name=self.preset_name)

    def as_dict(self) -> dict[str, object]:
        return {
            "enabled_toggles": [t.value for t in sorted(self.enabled_toggles, key=lambda x: x.value)],
            "scope": self.scope,
            "preset_name": self.preset_name,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> QoLSettings:
        raw_toggles = data.get("enabled_toggles", [])
        toggles: set[QoLToggle] = set()
        if isinstance(raw_toggles, Iterable) and not isinstance(raw_toggles, str | bytes):
            for value in raw_toggles:
                if isinstance(value, QoLToggle):
                    toggles.add(value)
                elif isinstance(value, str) and value in _QOL_TOGGLE_VALUES:
                    toggles.add(QoLToggle(value))

        scope = data.get("scope")
        preset_name = data.get("preset_name")
        return cls(
            enabled_toggles=toggles,
            scope=scope if isinstance(scope, str) else "session",
            preset_name=preset_name if isinstance(preset_name, str) else None,
        )


def _preset(name: str, toggles: tuple[QoLToggle, ...]) -> QoLSettings:
    return QoLSettings(enabled_toggles=set(toggles), scope="preset", preset_name=name)


BUILTIN_PRESETS: dict[str, QoLSettings] = {
    "silent": _preset(
        "silent",
        (
            QoLToggle.NO_THINKING,
            QoLToggle.NO_CHAT,
            QoLToggle.MINIMAL,
        ),
    ),
    "code-only": _preset(
        "code-only",
        (
            QoLToggle.FILE_ONLY,
            QoLToggle.NO_CHAT,
            QoLToggle.NO_MARKDOWN,
        ),
    ),
    "structured": _preset(
        "structured",
        (
            QoLToggle.STRUCTURED_ONLY,
            QoLToggle.NO_CHAT,
        ),
    ),
    "audit": _preset(
        "audit",
        (
            QoLToggle.APPEND_AUDIT_TRAIL,
            QoLToggle.REDACT_SECRETS,
        ),
    ),
    "plain-text": _preset(
        "plain-text",
        (QoLToggle.NO_MARKDOWN,),
    ),
}
