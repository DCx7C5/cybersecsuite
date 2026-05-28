from tortoise import fields, models
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from .enums import ApprovalStatus


class ApprovalRequest(BaseModel, TimestampMixin):
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="approval_requests",
        on_delete=fields.CASCADE,
    )
    session_id = fields.CharField(max_length=128, db_index=True)
    agent_id = fields.CharField(max_length=128, db_index=True)
    action_type = fields.CharField(max_length=64, db_index=True)
    action_payload = fields.JSONField(default=dict)
    status = fields.CharEnumField(
        ApprovalStatus,
        default=ApprovalStatus.PENDING,
        db_index=True,
    )
    expires_at = fields.DatetimeField(
        null=True,
        help_text="Deadline after which PENDING requests auto-expire",
    )
    decision_actor = fields.CharField(max_length=128, null=True)
    decision_reason = fields.TextField(default="")
    decided_at = fields.DatetimeField(null=True)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "approval_requests"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization_id", "status", "created_at"]),  # type: ignore[reportPrivateImportUsage]
            models.Index(fields=["organization_id", "session_id"]),  # type: ignore[reportPrivateImportUsage]
            models.Index(fields=["expires_at"]),  # type: ignore[reportPrivateImportUsage]
        ]

