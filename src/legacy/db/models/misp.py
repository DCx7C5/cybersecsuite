"""MISP intelligence models normalized from feed snapshots."""

from tortoise import fields
from css.core.db.models.base import BaseModel


class MISPEventIntel(BaseModel):
    """Normalized MISP event metadata."""

    id = fields.BigIntField(primary_key=True)
    event_uuid = fields.CharField(max_length=64, unique=True, db_index=True)
    event_id = fields.CharField(max_length=64, null=True, db_index=True)
    info = fields.CharField(max_length=512, default="", db_index=True)
    analysis = fields.CharField(max_length=64, default="")
    threat_level = fields.CharField(max_length=64, default="", db_index=True)
    distribution = fields.CharField(max_length=64, default="")
    published = fields.BooleanField(default=False, db_index=True)
    orgc_name = fields.CharField(max_length=255, default="")
    org_name = fields.CharField(max_length=255, default="")
    tags = fields.JSONField(default=list)
    attribute_count = fields.IntField(default=0)
    first_seen = fields.DatetimeField(null=True)
    last_seen = fields.DatetimeField(null=True)
    published_at = fields.DatetimeField(null=True)
    source_file = fields.CharField(max_length=500, default="")
    source_snapshot = fields.ForeignKeyField(
        "models.ThreatIntelFeedSnapshot",
        related_name="misp_events",
        null=True,
        on_delete=fields.SET_NULL,
    )
    raw_record = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_misp_events"
        ordering = ["-updated_at"]
        indexes = (("published",), ("orgc_name",), ("threat_level",))


class MISPAttributeIntel(BaseModel):
    """Normalized MISP attributes extracted from events."""

    id = fields.BigIntField(primary_key=True)
    attribute_uuid = fields.CharField(max_length=64, unique=True, db_index=True)
    event = fields.ForeignKeyField("models.MISPEventIntel", related_name="attributes", on_delete=fields.CASCADE)
    attribute_id = fields.CharField(max_length=64, null=True, db_index=True)
    category = fields.CharField(max_length=128, default="", db_index=True)
    attribute_type = fields.CharField(max_length=128, default="", db_index=True)
    normalized_ioc_type = fields.CharField(max_length=64, default="", db_index=True)
    value = fields.CharField(max_length=2000, db_index=True)
    comment = fields.TextField(null=True)
    to_ids = fields.BooleanField(default=False, db_index=True)
    deleted = fields.BooleanField(default=False, db_index=True)
    distribution = fields.CharField(max_length=64, default="")
    first_seen = fields.DatetimeField(null=True)
    last_seen = fields.DatetimeField(null=True)
    tags = fields.JSONField(default=list)
    source_file = fields.CharField(max_length=500, default="")
    source_snapshot = fields.ForeignKeyField(
        "models.ThreatIntelFeedSnapshot",
        related_name="misp_attributes",
        null=True,
        on_delete=fields.SET_NULL,
    )
    raw_record = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_misp_attributes"
        ordering = ["-updated_at"]
        indexes = (("attribute_type",), ("normalized_ioc_type",), ("to_ids",), ("deleted",), ("value",))

