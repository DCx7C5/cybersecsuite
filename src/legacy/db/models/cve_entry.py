"""Line-level CVE intelligence entry model."""

from tortoise import fields
from css.core.db.models.base import BaseModel
from css.core.db.fields import DescriptionField


class CVEIntelligenceEntry(BaseModel):
    """Line/item entries from cve-intelligence.md (history can include duplicates)."""

    id = fields.BigIntField(primary_key=True)
    cve = fields.ForeignKeyField("models.CVEIntel", related_name="intelligence_entries", null=True)
    cve_identifier = fields.CharField(max_length=32)
    score = fields.FloatField(null=True)
    description = DescriptionField(null=True)
    published_at = fields.DatetimeField(null=True)
    line_number = fields.IntField(null=True)
    source_file = fields.CharField(max_length=500, default="data/cybersec-shared/intelligence/cve-intelligence.md")
    raw_record = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "intel_cve_entries"
        indexes = (("cve_identifier",), ("published_at",), ("line_number",))

