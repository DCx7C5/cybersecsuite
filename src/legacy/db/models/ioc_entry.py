"""IOC knowledge database entry model."""

from tortoise import fields
from css.core.db.models.base import BaseModel


class IOCDatabaseEntry(BaseModel):
    """IOC knowledge entries from ioc-db.md (or future structured exports)."""

    id = fields.BigIntField(primary_key=True)
    ioc_type = fields.CharField(max_length=64)
    value = fields.CharField(max_length=2000)
    confidence = fields.CharField(max_length=32, null=True)
    tags = fields.JSONField(default=list)
    context = fields.TextField(null=True)
    first_seen = fields.DatetimeField(null=True)
    last_seen = fields.DatetimeField(null=True)
    source_file = fields.CharField(max_length=500, default="data/cybersec-shared/intelligence/ioc-db.md")
    raw_record = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_ioc_db_entries"
        unique_together = (("ioc_type", "value"),)
        indexes = (("ioc_type",), ("value",), ("first_seen",), ("last_seen",))


