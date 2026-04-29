"""
Threat Intelligence Models

All reference/intelligence data (CVE, CWE, MITRE, Threat Profiles) lives here.
These are canonical knowledge-base records, not scoped operational data.
"""

from tortoise.models import Model
from tortoise import fields

from db.models.enums import Confidence, ConfidenceLevel, ThreatActorSophistication, MITRETactic


# ----------------------------------------------------------------------
# Threat Actor / Profile
# ----------------------------------------------------------------------
class ThreatProfile(Model):
    """Threat actor intelligence profile."""
    id = fields.BigIntField(primary_key=True)
    actor_name = fields.CharField(max_length=255, db_index=True)
    sophistication = fields.CharEnumField(ThreatActorSophistication, default=ThreatActorSophistication.UNKNOWN, db_index=True)
    attribution_confidence = fields.CharEnumField(Confidence, default=Confidence.LOW, db_index=True)
    known_capabilities = fields.JSONField(default=list)
    known_infrastructure = fields.JSONField(default=list)
    observed_ttps = fields.JSONField(default=list)
    adversary_tooling = fields.JSONField(default=list)
    motivation = fields.CharField(max_length=128, default="")
    origin_country = fields.CharField(max_length=3, default="")
    assessment_text = fields.TextField(default="")
    notes = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "threat_profiles"
        table_description_plural = "Threat Profiles"
        table_description_singular = "Threat Profile"
        ordering = ["-updated_at"]


class ForensicMITRETechnique(Model):
    """Operational MITRE technique catalog used by forensic sessions and findings."""
    id = fields.BigIntField(primary_key=True)
    technique_id = fields.CharField(max_length=32, unique=True, db_index=True)
    technique_name = fields.CharField(max_length=255, db_index=True)
    tactic = fields.CharEnumField(MITRETactic, db_index=True)
    sub_tactic = fields.CharField(max_length=128, default="")
    technique_description = fields.TextField(default="")
    platforms = fields.JSONField(default=list)
    data_sources = fields.JSONField(default=list)
    detection_notes = fields.TextField(default="")
    mitigation_notes = fields.TextField(default="")
    references = fields.JSONField(default=list)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "forensic_mitre_techniques"
        table_description_plural = "Forensic MITRE Techniques"
        table_description_singular = "Forensic MITRE Technique"
        ordering = ["technique_id"]


class IOCMITREMapping(Model):
    """Analyst-confirmed mapping between a forensic IOC and ATT&CK technique."""
    id = fields.BigIntField(primary_key=True)
    ioc = fields.ForeignKeyField("models.IOCEntry", related_name="mitre_mappings", on_delete=fields.CASCADE, db_index=True)
    technique = fields.ForeignKeyField("models.ForensicMITRETechnique", related_name="ioc_mappings", on_delete=fields.CASCADE, db_index=True)
    confidence = fields.CharEnumField(ConfidenceLevel, default=ConfidenceLevel.MEDIUM, db_index=True)
    mapping_source = fields.CharField(max_length=255, default="")
    rationale = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "ioc_mitre_mappings"
        table_description_plural = "IOC MITRE Mappings"
        table_description_singular = "IOC MITRE Mapping"
        unique_together = [("ioc_id", "technique_id")]
        indexes = [
            ("technique", "confidence"),
        ]

# ----------------------------------------------------------------------
# Re-exports for clean imports
# ----------------------------------------------------------------------
__all__ = [
    "ThreatProfile",
    "ForensicMITRETechnique",
    "IOCMITREMapping",
]
