"""Proof of Concept (PoC) model — links exploits/PoCs to CVE records."""

from tortoise import fields
from tortoise.models import Model

from db.models.enums import PocStatus, Severity


class ProofOfConcept(Model):
    """A known public PoC or exploit code linked to a CVE."""

    id = fields.BigIntField(primary_key=True)
    cve = fields.ForeignKeyField(
        "models.CVEIntel",
        related_name="poc_instances",
        db_index=True,
        null=True,
        on_delete=fields.SET_NULL,
    )
    title = fields.CharField(max_length=512, default="", db_index=True)
    description = fields.TextField(default="")
    poc_url = fields.CharField(max_length=2048, default="", db_index=True, description="Primary PoC / exploit URL.")
    source = fields.CharField(max_length=256, default="", description="ExploitDB, GitHub, PacketStorm, etc.")
    language = fields.CharField(max_length=64, default="", description="Primary language (python, c, ruby, …).")
    status = fields.CharEnumField(PocStatus, default=PocStatus.UNVERIFIED, db_index=True)
    severity = fields.CharEnumField(Severity, null=True, db_index=True)
    reliability_score = fields.FloatField(null=True, description="0.0–1.0; community reliability estimate.")
    is_weaponized = fields.BooleanField(default=False, db_index=True)
    requires_auth = fields.BooleanField(default=False)
    requires_interaction = fields.BooleanField(default=False)
    affected_versions = fields.JSONField(default=list, description="List of affected version strings.")
    tags = fields.JSONField(default=list)
    published_at = fields.DatetimeField(null=True, db_index=True)
    raw_record = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "intel_pocs"
        ordering = ["-published_at", "-created_at"]
        indexes = (
            ("cve_id", "status"),
            ("status", "is_weaponized"),
        )

    def __str__(self) -> str:
        return f"PoC({self.title or self.poc_url})"
