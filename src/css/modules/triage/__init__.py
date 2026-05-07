"""Triage: Background LLM for classification and routing."""

from css.core.logger import getLogger
from .engine import TriageEngine
from .models import TriageRequest, TriageResult
from .enums import TriageStatus, TriageCategory, TriageDecision, SeverityLevel
from .exceptions import (
    BaseTriageException,
    TriageExecutionError,
    TriageClassificationError,
)

logger = getLogger(__name__)

__all__ = [
    # Engine
    "TriageEngine",
    
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
]

logger.info("Triage module loaded")
