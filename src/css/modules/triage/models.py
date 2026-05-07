"""Triage request and response models."""

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime

from .enums import TriageStatus, TriageCategory, TriageDecision, SeverityLevel


@dataclass
class TriageRequest:
    """Request for triage classification."""
    query: str
    context: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TriageResult:
    """Result from triage classification."""
    request_id: str
    status: TriageStatus
    category: Optional[TriageCategory] = None
    decision: Optional[TriageDecision] = None
    severity: Optional[SeverityLevel] = None
    confidence: float = 0.0
    reasoning: str = ""
    routing_target: Optional[str] = None
    duration_ms: float = 0.0
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
