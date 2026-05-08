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