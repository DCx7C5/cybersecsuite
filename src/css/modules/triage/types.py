"""Structured triage runtime metadata types."""

import msgspec

from .enums import SeverityLevel, TriageCategory


class TriageMetadata(msgspec.Struct, frozen=True, kw_only=True):
    category: TriageCategory = TriageCategory.MODERATE
    severity: SeverityLevel = SeverityLevel.MEDIUM
    confidence: float = 0.0


__all__ = ["TriageMetadata"]
