"""
Timeline and forensic artifact models.
"""
from tortoise.models import Model
from tortoise import fields

from db.models.enums import Severity


class Timeline(Model):
    """Investigation timeline entries."""
    id = fields.BigIntField(primary_key=True)
    session = fields.ForeignKeyField("models.Session", related_name="timeline_entries", db_index=True)
    timestamp = fields.DatetimeField(db_index=True)
    phase = fields.CharField(max_length=64)
    event = fields.TextField()
    severity = fields.CharEnumField(Severity, default=Severity.INFO, db_index=True)
    ioc_reference = fields.ForeignKeyField("models.IOC", related_name="timeline_entries", null=True)
    artifact_reference = fields.CharField(max_length=500, null=True)
    command_reference = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "timeline_entries"
        table_description_plural = "Timeline Entries"
        ordering = ["timestamp"]


class ForensicArtifact(Model):
    """Collected forensic artifacts."""
    id = fields.BigIntField(primary_key=True)
    session = fields.ForeignKeyField("models.Session", related_name="artifacts", db_index=True)
    name = fields.CharField(max_length=255)
    artifact_type = fields.CharField(max_length=100, db_index=True)
    file_path = fields.CharField(max_length=1000)
    file_size = fields.BigIntField(null=True)
    sha256_hash = fields.CharField(max_length=64, db_index=True)
    collected_at = fields.DatetimeField(auto_now_add=True)
    collector = fields.CharField(max_length=255)
    custody_log = fields.JSONField(default=list)

    class Meta:
        table = "forensic_artifacts"
