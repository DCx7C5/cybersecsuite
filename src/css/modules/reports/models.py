"""Report persistence models."""

from tortoise import fields
from css.core.db.models.base import BaseModel


class ReportRecord(BaseModel):
    """Generated report metadata and payload."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="reports",
        on_delete=fields.CASCADE,
    )
    report_id = fields.CharField(max_length=64, unique=True, db_index=True)
    title = fields.CharField(max_length=255)
    report_type = fields.CharField(max_length=16, choices=["markdown", "html", "pdf"], db_index=True)
    source_type = fields.CharField(max_length=32, default="incident")
    source_id = fields.CharField(max_length=128, db_index=True)
    content = fields.TextField()
    generated_by = fields.CharField(max_length=255, default="system")
    generated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "reports"
        indexes = [("organization_id", "source_type", "source_id", "generated_at")]
