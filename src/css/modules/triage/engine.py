"""Triage classification and routing engine."""

import logging
from typing import Optional, Dict
from datetime import datetime
import uuid

from .models import TriageRequest, TriageResult
from .enums import TriageStatus, TriageCategory, TriageDecision, SeverityLevel
from .exceptions import TriageExecutionError

logger = logging.getLogger(__name__)


class TriageEngine:
    """Triage engine for classification and routing."""
    
    def __init__(self, ollama_client=None):
        """Initialize triage engine."""
        self.ollama_client = ollama_client
        self._results_cache: Dict[str, TriageResult] = {}
    
    async def classify(self, request: TriageRequest) -> TriageResult:
        """Classify a query and determine routing."""
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Simple classification logic (in production would use Ollama)
            category = await self._determine_category(request)
            decision = await self._determine_decision(request, category)
            severity = await self._determine_severity(request)
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = TriageResult(
                request_id=request_id,
                status=TriageStatus.COMPLETED,
                category=category,
                decision=decision,
                severity=severity,
                confidence=0.85,  # Placeholder
                reasoning=f"Classified as {category.value} - routing to {decision.value}",
                duration_ms=duration_ms
            )
            
            self._results_cache[request_id] = result
            logger.info(f"Triage completed: {request_id} ({duration_ms:.1f}ms)")
            
            return result
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = TriageResult(
                request_id=request_id,
                status=TriageStatus.FAILED,
                error=str(e),
                duration_ms=duration_ms
            )
            
            logger.error(f"Triage failed: {e}")
            raise TriageExecutionError(str(e))
    
    async def _determine_category(self, request: TriageRequest) -> TriageCategory:
        """Determine query complexity category."""
        query_len = len(request.query.split())
        
        if query_len < 10:
            return TriageCategory.SIMPLE
        elif query_len < 50:
            return TriageCategory.MODERATE
        else:
            return TriageCategory.COMPLEX
    
    async def _determine_decision(self, request: TriageRequest, category: TriageCategory) -> TriageDecision:
        """Determine routing decision."""
        if category == TriageCategory.SIMPLE:
            return TriageDecision.SKILL
        elif category == TriageCategory.MODERATE:
            return TriageDecision.AGENT
        elif category == TriageCategory.COMPLEX:
            return TriageDecision.TEAM
        else:
            return TriageDecision.ESCALATE
    
    async def _determine_severity(self, request: TriageRequest) -> SeverityLevel:
        """Determine severity level."""
        keywords = {
            'critical': SeverityLevel.CRITICAL,
            'emergency': SeverityLevel.CRITICAL,
            'urgent': SeverityLevel.HIGH,
            'high': SeverityLevel.HIGH,
            'medium': SeverityLevel.MEDIUM,
            'low': SeverityLevel.LOW,
        }
        
        query_lower = request.query.lower()
        for keyword, level in keywords.items():
            if keyword in query_lower:
                return level
        
        return SeverityLevel.MEDIUM
    
    def get_result(self, request_id: str) -> Optional[TriageResult]:
        """Get cached triage result."""
        return self._results_cache.get(request_id)
    
    def get_stats(self) -> Dict[str, any]:
        """Get triage statistics."""
        completed = sum(1 for r in self._results_cache.values() if r.status == TriageStatus.COMPLETED)
        failed = sum(1 for r in self._results_cache.values() if r.status == TriageStatus.FAILED)
        
        avg_duration = 0.0
        if completed > 0:
            total_duration = sum(r.duration_ms for r in self._results_cache.values() if r.status == TriageStatus.COMPLETED)
            avg_duration = total_duration / completed
        
        # Count by decision
        by_decision = {}
        for result in self._results_cache.values():
            if result.decision:
                decision_key = result.decision.value
                by_decision[decision_key] = by_decision.get(decision_key, 0) + 1
        
        return {
            "total": len(self._results_cache),
            "completed": completed,
            "failed": failed,
            "avg_duration_ms": avg_duration,
            "by_decision": by_decision,
        }
