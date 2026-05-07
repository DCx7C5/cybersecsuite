"""Incidents module — incident lifecycle management (Phase 7).

Models:
- Incident: Core incident record (id, title, severity, status, timeline)
- IncidentTimeline: Append-only event log for incident progression
- IncidentTask: Task items within incident (investigation, containment, recovery)
"""

from tortoise import Model, fields
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    """Incident severity classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Incident lifecycle status."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    REMEDIATED = "remediated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class IncidentSource(str, Enum):
    """How incident was detected."""
    ALERT = "alert"
    SCAN = "scan"
    MANUAL_REPORT = "manual_report"
    THREAT_INTEL = "threat_intel"
    HUNT = "hunt"
    LOG_ANALYSIS = "log_analysis"
    EDR = "edr"
    OTHER = "other"


class TimelineEventType(str, Enum):
    """Incident timeline event types."""
    CREATED = "created"
    UPDATED = "updated"
    ESCALATED = "escalated"
    ASSIGNED = "assigned"
    STATUS_CHANGED = "status_changed"
    INVESTIGATION_STARTED = "investigation_started"
    CONTAINMENT_STARTED = "containment_started"
    CONTAINMENT_COMPLETED = "containment_completed"
    REMEDIATION_STARTED = "remediation_started"
    REMEDIATION_COMPLETED = "remediation_completed"
    RESOLVED = "resolved"
    CLOSED = "closed"
    COMMENT = "comment"


class Incident(Model):
    """Incident — security event requiring response."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="incidents",
        on_delete=fields.CASCADE,
    )
    
    # Identification
    incident_id = fields.CharField(
        max_length=64,
        db_index=True,
        unique_together=("organization",),
        help_text="e.g., INC-2024-001"
    )
    
    # Description
    title = fields.CharField(max_length=255)
    description = fields.TextField(default="")
    
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
    root_cause = fields.TextField(
        default="",
        help_text="Post-incident analysis of root cause"
    )
    lessons_learned = fields.TextField(
        default="",
        help_text="What we learned / improvements made"
    )
    
    # Metadata
    created_by = fields.CharField(max_length=255, default="system")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "incidents"
        unique_together = (("organization", "incident_id"),)
        indexes = [
            fields.Index(["organization", "status", "-detected_at"]),
            fields.Index(["organization", "severity", "-detected_at"]),
            fields.Index(["assigned_team_id", "status"]),
        ]


class IncidentTimeline(Model):
    """Append-only incident progression log."""
    
    id = fields.BigIntField(primary_key=True)
    incident: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Incident",
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
    description = fields.TextField(default="")
    
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
    
    class Meta:
        table = "incident_timeline"
        unique_together = (("incident", "sequence_number"),)
        ordering = ["incident", "sequence_number"]


class IncidentTask(Model):
    """Task items within incident investigation/containment/remediation."""
    
    id = fields.BigIntField(primary_key=True)
    incident: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Incident",
        related_name="tasks",
        on_delete=fields.CASCADE,
    )
    
    # Task definition
    title = fields.CharField(max_length=255)
    description = fields.TextField(default="")
    
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
    
    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "incident_tasks"
        ordering = ["-priority", "due_date"]
        indexes = [
            fields.Index(["incident", "status"]),
            fields.Index(["assigned_to", "status"]),
        ]


__all__ = [
    "SeverityLevel",
    "IncidentStatus",
    "IncidentSource",
    "TimelineEventType",
    "Incident",
    "IncidentTimeline",
    "IncidentTask",
]
