"""Evidence module — forensic chain-of-custody tracking (Phase 7).

Models:
- Evidence: Individual evidence item (hash, source, collector, timestamps)
- EvidenceChain: Immutable append-only transaction log (events via EventStore)
- EvidenceTagging: Tag evidence by incident/case/type
"""

from tortoise import fields, models
from css.core.db.fields import DescriptionField, QualityScoreField
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from .enums import EvidenceStatus, EvidenceType, ChainEventType


class Evidence(BaseModel, TimestampMixin):
    """Individual evidence item — forensic artifact."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="evidence_items",
        on_delete=fields.CASCADE,
    )
    
    # Case linkage
    case_id = fields.CharField(
        max_length=255,
        db_index=True,
        help_text="Investigation case ID"
    )
    
    # Evidence identification
    evidence_id = fields.CharField(
        max_length=255,
        db_index=True,
        help_text="Unique evidence identifier (e.g., EV-2024-001)"
    )
    
    # Content addressing
    hash_sha256 = fields.CharField(
        max_length=64,
        db_index=True,
        unique=True,
        help_text="SHA256 hash of evidence content"
    )
    hash_md5 = fields.CharField(
        max_length=32,
        null=True,
        help_text="MD5 hash for legacy compatibility"
    )
    
    # Source information
    evidence_type = fields.CharField(
        max_length=32,
        choices=[t.value for t in EvidenceType],
        db_index=True,
    )
    source = fields.CharField(
        max_length=512,
        help_text="Source of evidence (file path, IP, hostname, etc.)"
    )
    source_agent_id = fields.CharField(
        max_length=255,
        db_index=True,
        help_text="ID of collecting agent/tool"
    )
    
    # Descriptive information
    description = DescriptionField(default="")
    tags = fields.JSONField(default=list, help_text="Searchable tags (incident_type, severity, etc.)")
    
    # Physical properties
    size_bytes = fields.BigIntField(null=True)
    mime_type = fields.CharField(max_length=64, null=True)
    
    # Status
    status = fields.CharField(
        max_length=32,
        choices=[s.value for s in EvidenceStatus],
        default="collected",
        db_index=True,
    )
    
    # Chain of custody tracking
    collected_by = fields.CharField(max_length=255)
    collected_at = fields.DatetimeField(db_index=True)
    
    # Sealing for immutability
    is_sealed = fields.BooleanField(default=False, db_index=True)
    sealed_at = fields.DatetimeField(null=True)
    seal_signature = fields.TextField(
        default="",
        help_text="Cryptographic signature of sealed content"
    )
    
    # Access controls
    access_level = fields.CharField(
        max_length=32,
        default="restricted",
        choices=["public", "internal", "restricted", "confidential"],
        help_text="Evidence classification level"
    )
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "evidence"
        unique_together = (("organization_id", "evidence_id"),)
        indexes = [
            models.Index(fields=["organization_id", "case_id", "status"]),  # type: ignore[reportPrivateImportUsage]
            models.Index(fields=["organization_id", "evidence_type"]),  # type: ignore[reportPrivateImportUsage]
            models.Index(fields=["source_agent_id", "collected_at"]),  # type: ignore[reportPrivateImportUsage]
        ]


class EvidenceChain(BaseModel):
    """Immutable chain-of-custody transaction log."""

    evidence: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Evidence",
        related_name="chain_events",
        on_delete=fields.CASCADE,
    )
    
    # Event sequence (append-only)
    sequence_number = fields.IntField(db_index=True, help_text="Sequential number within chain")
    event_type = fields.CharField(
        max_length=32,
        choices=[e.value for e in ChainEventType],
        db_index=True,
    )
    
    # Actor information
    actor = fields.CharField(max_length=255, help_text="User/system that performed action")
    actor_id = fields.CharField(max_length=255, null=True)
    
    # Event details
    action = fields.CharField(max_length=512, help_text="Description of action taken")
    metadata = fields.JSONField(
        default=dict,
        help_text={"location": "...", "recipient": "...", "duration_seconds": 123}
    )
    
    # Verification
    hash_before = fields.CharField(
        max_length=64,
        help_text="Hash of evidence before this action"
    )
    hash_after = fields.CharField(
        max_length=64,
        help_text="Hash of evidence after this action (unchanged unless modified)"
    )
    
    # Event integrity
    event_signature = fields.TextField(
        help_text="Cryptographic signature of this event"
    )
    previous_signature = fields.TextField(
        null=True,
        help_text="Signature of previous event (chain link)"
    )
    
    # Timestamps
    occurred_at = fields.DatetimeField(db_index=True)
    recorded_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "evidence_chain"
        unique_together = (("evidence_id", "sequence_number"),)
        ordering = ["evidence_id", "sequence_number"]
        indexes = [
            models.Index(fields=["evidence_id", "event_type"]),  # type: ignore[reportPrivateImportUsage]
            models.Index(fields=["actor_id", "occurred_at"]),  # type: ignore[reportPrivateImportUsage]
        ]


class EvidenceTagging(BaseModel, TimestampMixin):
    """Tag evidence by incident, case, or classification."""

    evidence: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Evidence",
        related_name="incident_tags",
        on_delete=fields.CASCADE,
    )
    
    # Linking
    incident_id = fields.CharField(
        max_length=255,
        null=True,
        db_index=True,
        help_text="Incident this evidence relates to"
    )
    case_id = fields.CharField(
        max_length=255,
        null=True,
        db_index=True,
        help_text="Investigation case"
    )
    
    # Relevance
    relevance_score = QualityScoreField(
        default=0.0,
        help_text="How relevant to incident/case (0.0-1.0)"
    )
    notes = fields.TextField(default="")
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "evidence_tagging"
        unique_together = (("evidence_id", "incident_id"),)

