"""OpenCTI intelligence models normalized from exported feeds."""

from tortoise import fields
from tortoise.models import Model


class OpenCTIIndicatorIntel(Model):
    """Normalized OpenCTI indicators."""

    id = fields.BigIntField(primary_key=True)
    stix_id = fields.CharField(max_length=128, unique=True, db_index=True, null=True)
    opencti_id = fields.CharField(max_length=128, unique=True, db_index=True, null=True)
    indicator_type = fields.CharField(max_length=64, default="", db_index=True)
    name = fields.CharField(max_length=255, default="", db_index=True)
    description = fields.TextField(null=True)
    pattern = fields.TextField()
    pattern_type = fields.CharField(max_length=64, default="")
    indicator_types = fields.JSONField(default=list)
    observable_values = fields.JSONField(default=list)
    confidence = fields.IntField(null=True)
    score = fields.FloatField(null=True)
    valid_from = fields.DatetimeField(null=True)
    valid_until = fields.DatetimeField(null=True)
    labels = fields.JSONField(default=list)
    created_by = fields.CharField(max_length=255, default="")
    revoked = fields.BooleanField(default=False, db_index=True)
    source_file = fields.CharField(max_length=500, default="")
    source_snapshot = fields.ForeignKeyField(
        "models.ThreatIntelFeedSnapshot",
        related_name="opencti_indicators",
        null=True,
        on_delete=fields.SET_NULL,
    )
    raw_record = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_opencti_indicators"
        ordering = ["-updated_at"]
        indexes = (("name",), ("pattern_type",), ("revoked",))


class OpenCTIEntityIntel(Model):
    """Normalized non-indicator STIX/OpenCTI entities."""

    id = fields.BigIntField(primary_key=True)
    stix_id = fields.CharField(max_length=128, unique=True, db_index=True, null=True)
    opencti_id = fields.CharField(max_length=128, unique=True, db_index=True, null=True)
    entity_type = fields.CharField(max_length=64, db_index=True)
    name = fields.CharField(max_length=255, default="", db_index=True)
    description = fields.TextField(null=True)
    aliases = fields.JSONField(default=list)
    labels = fields.JSONField(default=list)
    confidence = fields.IntField(null=True)
    first_seen = fields.DatetimeField(null=True)
    last_seen = fields.DatetimeField(null=True)
    created_by = fields.CharField(max_length=255, default="")
    external_references = fields.JSONField(default=list)
    source_file = fields.CharField(max_length=500, default="")
    source_snapshot = fields.ForeignKeyField(
        "models.ThreatIntelFeedSnapshot",
        related_name="opencti_entities",
        null=True,
        on_delete=fields.SET_NULL,
    )
    raw_record = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_opencti_entities"
        ordering = ["entity_type", "name"]
        indexes = (("entity_type",), ("name",), ("confidence",))

