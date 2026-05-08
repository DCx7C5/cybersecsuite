"""CWE intelligence model."""

from tortoise import fields
from css.core.db.models.base import BaseModel
from css.core.db.fields import DescriptionField


class CWEIntel(BaseModel):
    """Canonical CWE weakness definitions from CWE feeds/XML extractions."""

    id = fields.BigIntField(primary_key=True)
    cwe_id = fields.CharField(max_length=32, unique=True, db_index=True)
    name = fields.CharField(max_length=255, db_index=True)
    abstraction = fields.CharField(max_length=64, null=True, db_index=True, description="Pillar/Class/Base/Variant.")
    status = fields.CharField(max_length=64, null=True, db_index=True)
    description = DescriptionField(null=True)
    extended_description = fields.TextField(null=True)
    likelihood_of_exploit = fields.CharField(max_length=64, null=True, description="High/Medium/Low.")
    common_consequences = fields.JSONField(default=list)
    detection_methods = fields.JSONField(default=list)
    mitigations = fields.JSONField(default=list)
    related_attack_patterns = fields.JSONField(default=list, description="CAPEC IDs.")
    source_file = fields.CharField(max_length=500, null=True)
    raw_record = fields.JSONField(default=dict)
    tags = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_cwes"
        ordering = ["cwe_id"]
        indexes = (("cwe_id",), ("name",), ("status",), ("abstraction",))

    def __str__(self):
        return f"{self.cwe_id}: {self.name}"
