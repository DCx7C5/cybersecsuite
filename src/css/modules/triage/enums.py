"""Triage enumerations."""

from enum import Enum


class TriageStatus(str, Enum):
    """Status of a triage task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TriageCategory(str, Enum):
    """Categories for triage classification."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"


class TriageDecision(str, Enum):
    """Routing decisions from triage."""
    AGENT = "agent"
    TEAM = "team"
    SKILL = "skill"
    QUEUE = "queue"
    ESCALATE = "escalate"


class SeverityLevel(str, Enum):
    """Severity levels for triage."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
