"""QoL Output Controls — msgspec.Struct models.

QoLToggle   — individual boolean switch
QoLSettings — aggregated per-scope configuration as immutable msgspec.Struct
"""

from enum import Enum
from typing import Any

import msgspec


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

    def activate(self, *toggles: QoLToggle | str) -> "QoLSettings":
        new_set = set(self.enabled_toggles)
        for t in toggles:
            new_set.add(QoLToggle(t) if isinstance(t, str) else t)
        return QoLSettings(enabled_toggles=new_set, scope=self.scope, preset_name=self.preset_name)

    def deactivate(self, *toggles: QoLToggle | str) -> "QoLSettings":
        new_set = set(self.enabled_toggles)
        for t in toggles:
            new_set.discard(QoLToggle(t) if isinstance(t, str) else t)
        return QoLSettings(enabled_toggles=new_set, scope=self.scope, preset_name=self.preset_name)

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
                pass
        return cls(
            enabled_toggles=toggles,
            scope=data.get("scope", "session"),
            preset_name=data.get("preset_name"),
        )
