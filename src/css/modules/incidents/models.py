"""Incidents module — incident lifecycle management (Phase 7).

Models:
- Incident: Core incident record (id, title, severity, status, timeline)
- IncidentTimeline: Append-only event log for incident progression
- IncidentTask: Task items within incident (investigation, containment, recovery)
"""

from tortoise import fields
from tortoise.indexes import Index

from css.core.db.fields import DescriptionField
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from css.modules.incidents.enums import IncidentSource, SeverityLevel, IncidentStatus, TimelineEventType


class Incident(BaseModel, TimestampMixin):
    """Incident — security event requiring response."""
    
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Organization",
        related_name="incidents",
        on_delete=fields.CASCADE,
    )
    
    # Identification
    incident_id = fields.CharField(
        max_length=64,
        db_index=True,
        unique_together=("organization_id",),
        help_text="e.g., INC-2024-001"
    )
    
    # Description
    title = fields.CharField(max_length=255)
    description = DescriptionField(default="")
    
    # Classification
    severity = fields.CharField(
        max_length=16,
        choices=[s.value for s in SeverityLevel],
        default="medium",
        db_index=True,
    )
    source = fields.CharField(
        max_length=32,
        choices=[s.value for s in IncidentSource],
        db_index=True,
    )
    
    # Detection
    detected_at = fields.DatetimeField(db_index=True)
    detection_method = fields.CharField(max_length=255, default="")
    
    # Status
    status = fields.CharField(
        max_length=32,
        choices=[s.value for s in IncidentStatus],
        default="open",
        db_index=True,
    )
    
    # Impact
    affected_assets = fields.JSONField(
        default=list,
        help_text="List of hostnames, IPs, user IDs affected"
    )
    affected_data_types = fields.JSONField(
        default=list,
        help_text="Customer, financial, healthcare, etc."
    )
    
    # Response
    assigned_team_id = fields.CharField(
        max_length=255,
        null=True,
        db_index=True,
        help_text="Response team ID"
    )
    assigned_to = fields.CharField(
        max_length=255,
        null=True,
        help_text="Primary incident handler"
    )
    
    # Lifecycle timestamps
    first_detection_at = fields.DatetimeField()
    investigation_started_at = fields.DatetimeField(null=True)
    containment_completed_at = fields.DatetimeField(null=True)
    remediation_completed_at = fields.DatetimeField(null=True)
    resolved_at = fields.DatetimeField(null=True)
    closed_at = fields.DatetimeField(null=True)
    
    # Metrics
    time_to_detect_minutes = fields.IntField(null=True)
    time_to_contain_minutes = fields.IntField(null=True)
    time_to_remediate_minutes = fields.IntField(null=True)
    
    # Linkage
    parent_incident_id = fields.BigIntField(
        null=True,
        help_text="If this is related to another incident"
    )
    related_evidence_ids = fields.JSONField(
        default=list,
        help_text="Evidence IDs collected for this incident"
    )
    related_scan_ids = fields.JSONField(
        default=list,
        help_text="Scan IDs that discovered or informed this incident"
    )
    
    # Analysis
    root_cause = DescriptionField(
        default="",
        help_text="Post-incident analysis of root cause"
    )
    lessons_learned = DescriptionField(
        default="",
        help_text="What we learned / improvements made"
    )
    
    created_by = fields.CharField(max_length=255, default="system")
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "incidents"
        unique_together = (("organization_id", "incident_id"),)
        indexes = [
            Index(fields=["organization_id", "status", "detected_at"]),
            Index(fields=["organization_id", "severity", "detected_at"]),
            Index(fields=["assigned_team_id", "status"]),
        ]


class IncidentTimeline(BaseModel):
    """Append-only incident progression log."""

    incident: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Incident",
        related_name="timeline_events",
        on_delete=fields.CASCADE,
    )
    
    # Event sequence
    sequence_number = fields.IntField(db_index=True)
    event_type = fields.CharField(
        max_length=32,
        choices=[e.value for e in TimelineEventType],
        db_index=True,
    )
    
    # Actor
    actor = fields.CharField(max_length=255, default="system")
    actor_id = fields.CharField(max_length=255, null=True)
    
    # Details
    title = fields.CharField(max_length=255)
    description = DescriptionField(default="")
    
    # Context (varies by event_type)
    metadata = fields.JSONField(
        default=dict,
        help_text={
            "status_changed": {"from": "open", "to": "investigating"},
            "escalated": {"from_severity": "medium", "to_severity": "high"},
            "assigned": {"team_id": "team-123", "handler": "alice"},
        }
    )
    
    # Attachment
    attachment_urls = fields.JSONField(
        default=list,
        help_text="Evidence URLs, screenshot URLs, etc."
    )
    
    # Timestamps
    occurred_at = fields.DatetimeField(db_index=True)
    recorded_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "incident_timeline"
        unique_together = (("incident_id", "sequence_number"),)
        ordering = ["incident", "sequence_number"]


class IncidentTask(BaseModel, TimestampMixin):
    """Task items within incident investigation/containment/remediation."""

    incident: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Incident",
        related_name="tasks",
        on_delete=fields.CASCADE,
    )
    
    # Task definition
    title = fields.CharField(max_length=255)
    description = DescriptionField(default="")
    
    # Task type/phase
    task_type = fields.CharField(
        max_length=32,
        choices=["triage", "investigation", "containment", "remediation", "recovery", "forensics"],
        db_index=True,
    )
    
    # Status
    status = fields.CharField(
        max_length=32,
        choices=["pending", "in_progress", "completed", "blocked", "cancelled"],
        default="pending",
        db_index=True,
    )
    
    # Assignment
    assigned_to = fields.CharField(max_length=255, null=True)
    owner_id = fields.CharField(max_length=255, null=True)
    
    # Priority
    priority = fields.CharField(
        max_length=16,
        choices=["low", "medium", "high", "critical"],
        default="medium",
    )
    
    # Estimation
    estimated_hours = fields.FloatField(null=True)
    actual_hours = fields.FloatField(null=True)
    
    # Dates
    due_date = fields.DatetimeField(null=True)
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    

    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "incident_tasks"
        ordering = ["-priority", "due_date"]
        indexes = [
            Index(fields=["incident_id", "status"]),
            Index(fields=["assigned_to", "status"]),
        ]
