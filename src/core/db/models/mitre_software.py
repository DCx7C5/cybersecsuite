"""MITRE ATT&CK software family intelligence model."""

from tortoise import fields
from tortoise.models import Model


class MitreSoftwareFamilyIntel(Model):
    """Canonical ATT&CK malware/tool families for hunting and detection workflows."""

    id = fields.BigIntField(primary_key=True)
    software_id = fields.CharField(max_length=32, unique=True, db_index=True)
    name = fields.CharField(max_length=255, db_index=True)
    software_type = fields.CharField(max_length=32, db_index=True, description="malware or tool")
    description = fields.TextField(null=True)
    aliases = fields.JSONField(default=list)
    platforms = fields.JSONField(default=list)
    domains = fields.JSONField(default=list)
    labels = fields.JSONField(default=list)
    is_family = fields.BooleanField(default=False, db_index=True)
    vendor = fields.CharField(max_length=255, default="")
    url = fields.CharField(max_length=512, default="")
    source_file = fields.CharField(max_length=500, null=True)
    raw_record = fields.JSONField(default=dict)
    tags = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_mitre_software_families"
        ordering = ["software_id"]
        indexes = (("software_id",), ("name",), ("software_type",), ("is_family",))

    def __str__(self):
        return f"{self.software_id}: {self.name}"

