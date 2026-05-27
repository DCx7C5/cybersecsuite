"""QoL settings persistence model."""

from tortoise import fields
from tortoise.indexes import Index

from css.core.db.fields import LabelField, StringListField
from css.core.settings.qol import QoLSettings, QoLToggle
from .base import BaseModel

_KNOWN_QOL_TOGGLES: set[str] = {toggle.value for toggle in QoLToggle}


def _encode_toggles(toggles: set[QoLToggle]) -> list[str]:
    return sorted(toggle.value for toggle in toggles)


def _decode_toggles(values: list[str] | None) -> set[QoLToggle]:
    if values is None:
        return set()
    decoded: set[QoLToggle] = set()
    for value in values:
        if value in _KNOWN_QOL_TOGGLES:
            decoded.add(QoLToggle(value))
    return decoded


class QoLSettingsModel(BaseModel):
    """Persisted QoL settings per user and scope."""

    user_id = LabelField(max_length=128, db_index=True)
    scope = LabelField(max_length=32, db_index=True)
    scope_id = LabelField(max_length=256, default="", db_index=True)
    enabled_toggles = StringListField(default=list)
    preset_name = fields.CharField(max_length=128, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def to_settings(self) -> QoLSettings:
        return QoLSettings(
            enabled_toggles=_decode_toggles(self.enabled_toggles),
            scope=self.scope,
            preset_name=self.preset_name,
        )

    @classmethod
    def from_settings(
        cls,
        *,
        user_id: str,
        scope: str,
        scope_id: str | None,
        settings: QoLSettings,
    ) -> "QoLSettingsModel":
        return cls(
            user_id=user_id,
            scope=scope,
            scope_id=scope_id or "",
            enabled_toggles=_encode_toggles(settings.enabled_toggles),
            preset_name=settings.preset_name,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "qol_settings"
        ordering = ["scope", "scope_id", "id"]
        unique_together = [("user_id", "scope", "scope_id")]
        indexes = [
            Index(fields=["user_id", "scope", "scope_id"]),
            Index(fields=["scope", "scope_id"]),
        ]

