"""Triage: Background LLM for classification and routing."""

from .engine import TriageEngine, classify_query
from .models import TriageRequest, TriageResult
from .enums import TriageStatus, TriageCategory, TriageDecision, SeverityLevel
from css.core.logger import getLogger
from .exceptions import (
    BaseTriageException,
    TriageExecutionError,
    TriageClassificationError,
)
# Phase 6 T6.5: Pipeline stages
from .pipeline import ClassifyStage, classify

logger = getLogger(__name__)

__all__ = [
    # Engine
    "TriageEngine",
    "classify_query",

    # Models
    "TriageRequest",
    "TriageResult",

    # Enums
    "TriageStatus",
    "TriageCategory",
    "TriageDecision",
    "SeverityLevel",

    # Exceptions
    "BaseTriageException",
    "TriageExecutionError",
    "TriageClassificationError",

    # Pipeline stages (Phase 6 T6.5)
    "ClassifyStage",
    "classify",
]

logger.info("Triage module loaded")
