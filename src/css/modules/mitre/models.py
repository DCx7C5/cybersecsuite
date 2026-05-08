"""MITRE ATT&CK module — threat framework mapping (Phase 7)."""

from tortoise import fields
from css.core.db.fields import DescriptionField
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from .enums import Tactic

class MITRETechnique(BaseModel, TimestampMixin):
    """MITRE ATT&CK technique."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="mitre_techniques",
        on_delete=fields.CASCADE,
    )
    
    # MITRE identifiers
    technique_id = fields.CharField(max_length=16, db_index=True)  # e.g., T1001
    subtechnique_id = fields.CharField(
        max_length=32,
        null=True,
        help_text="e.g., T1001.001"
    )
    
    tactic = fields.CharField(
        max_length=32,
        choices=[t.value for t in Tactic],
        db_index=True,
    )
    
    # Details
    name = fields.CharField(max_length=255)
    description = DescriptionField(default="")
    
    # References
    external_references = fields.JSONField(
        default=list,
        help_text="URLs to MITRE and other resources"
    )
    

    
    class Meta:
        table = "mitre_techniques"
        unique_together = (("organization", "technique_id", "subtechnique_id"),)
        indexes = [
            fields.Index(["organization", "tactic"]),
        ]


class ThreatActor(BaseModel, TimestampMixin):
    """Threat actor/campaign/group."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="threat_actors",
        on_delete=fields.CASCADE,
    )
    
    # Identification
    actor_name = fields.CharField(max_length=255, db_index=True)
    actor_aliases = fields.JSONField(
        default=list,
        help_text="Alternative names (Fancy Bear, APT28, etc.)"
    )
    
    # Classification
    actor_type = fields.CharField(
        max_length=32,
        choices=["nation_state", "criminal", "hacktivism", "insider", "unknown"],
        default="unknown",
    )
    
    # Tactics + Techniques (ATT&CK mapping)
    tactics = fields.JSONField(
        default=list,
        help_text="List of tactics used"
    )
    techniques = fields.JSONField(
        default=list,
        help_text="List of technique IDs used"
    )
    
    # Metadata
    description = DescriptionField(default="")
    targets = fields.JSONField(
        default=list,
        help_text="Industries/sectors targeted"
    )
    
    class Meta:
        table = "threat_actors"
        unique_together = (("organization", "actor_name"),)


class IncidentTechniqueMaping(BaseModel):
    """Link incident to ATT&CK techniques."""

    incident: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Incident",
        related_name="attck_mappings",
        on_delete=fields.CASCADE,
    )
    technique: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.MITRETechnique",
        related_name="incident_mappings",
        on_delete=fields.CASCADE,
    )
    
    # Evidence
    evidence = fields.TextField(
        help_text="How was this technique observed/confirmed"
    )
    confidence = fields.CharField(
        max_length=32,
        choices=["low", "medium", "high"],
        default="medium",
    )
    
    # Mapping metadata
    mapped_by = fields.CharField(max_length=255)
    mapped_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "incident_technique_mappings"
        unique_together = (("incident", "technique"),)


__all__ = [
    "Tactic",
    "MITRETechnique",
    "ThreatActor",
    "IncidentTechniqueMaping",
]
