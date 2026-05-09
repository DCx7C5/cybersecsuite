"""Triage request and response models."""
import msgspec

from typing import Any
from datetime import datetime, timezone

from .enums import TriageStatus, TriageCategory, TriageDecision, SeverityLevel

class TriageRequest(msgspec.Struct):
    """Request for triage classification."""
    query: str
    context: str = ""
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    created_at: datetime = msgspec.field(default_factory=lambda: datetime.now(timezone.utc))

class TriageResult(msgspec.Struct):
    """Result from triage classification."""
    request_id: str
    status: TriageStatus
    category: TriageCategory | None = None
    decision: TriageDecision | None = None
    severity: SeverityLevel | None = None
    confidence: float = 0.0
    reasoning: str = ""
    routing_target: str | None = None
    duration_ms: float = 0.0
    error: str | None = None
    created_at: datetime = msgspec.field(default_factory=datetime.utcnow)
