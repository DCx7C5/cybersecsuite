"""CVE intelligence model."""

from tortoise import fields
from tortoise.models import Model


class CVEIntel(Model):
    """Canonical CVE records from intelligence CVE feeds."""

    id = fields.BigIntField(primary_key=True)
    cve_id = fields.CharField(max_length=32, unique=True, db_index=True)
    cvss_score = fields.FloatField(null=True, db_index=True)
    cvss_vector = fields.CharField(max_length=128, default="", description="CVSS vector string.")
    severity = fields.CharField(max_length=16, default="", db_index=True, description="Derived: low/medium/high/critical.")
    description = fields.TextField(null=True)
    affected_products = fields.JSONField(default=list, description="CPE strings or product names.")
    references = fields.JSONField(default=list, description="External reference URLs.")
    exploit_available = fields.BooleanField(default=False, db_index=True)
    patch_available = fields.BooleanField(default=False, db_index=True)
    published_at = fields.DatetimeField(null=True, db_index=True)
    last_modified_at = fields.DatetimeField(null=True)
    source_file = fields.CharField(max_length=500, null=True)
    source_feed = fields.CharField(max_length=128, default="", description="NVD, MITRE, etc.")
    raw_record = fields.JSONField(default=dict)
    tags = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_cves"
        ordering = ["-published_at"]
        indexes = (
            ("cve_id",), ("published_at",), ("cvss_score",),
            ("severity",), ("exploit_available",),
        )

    @property
    def is_critical(self) -> bool:
        return self.cvss_score is not None and self.cvss_score >= 9.0

    def __str__(self):
        score = f" ({self.cvss_score})" if self.cvss_score else ""
        return f"{self.cve_id}{score}"
