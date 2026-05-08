"""MITRE technique intelligence model."""

from tortoise import fields
from css.core.db.models.base import BaseModel
from css.core.db.fields import DescriptionField, UrlField


class MitreTechniqueIntel(BaseModel):
    """MITRE ATT&CK techniques from shared MITRE technique snapshots."""

    id = fields.BigIntField(primary_key=True)
    technique_id = fields.CharField(max_length=32, unique=True, db_index=True)
    name = fields.CharField(max_length=255, db_index=True)
    description = DescriptionField(null=True)
    tactics = fields.JSONField(default=list, description="List of tactic IDs (TA0001, …).")
    platforms = fields.JSONField(default=list, description="linux, windows, macos, …")
    data_sources = fields.JSONField(default=list, description="Detection data sources.")
    is_sub_technique = fields.BooleanField(default=False, db_index=True)
    parent_technique_id = fields.CharField(max_length=32, default="", description="Parent ID if sub-technique.")
    detection = fields.TextField(null=True, description="Detection guidance from ATT&CK.")
    mitigation_refs = fields.JSONField(default=list, description="MITRE mitigation IDs.")
    url = UrlField(max_length=512, default="", description="ATT&CK URL.")
    source_file = fields.CharField(max_length=500, null=True)
    raw_record = fields.JSONField(default=dict)
    tags = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_mitre_techniques"
        ordering = ["technique_id"]
        indexes = (("technique_id",), ("name",), ("is_sub_technique",))

    def __str__(self):
        return f"{self.technique_id}: {self.name}"
