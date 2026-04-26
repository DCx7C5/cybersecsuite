"""
Worker Metrics and Monitoring API endpoints — t372.

Implements:
- GET /api/workers/{id}/metrics — Current metrics
- GET /api/workers/{id}/audit — Audit trail (paginated)
- GET /api/workers/summary?project_id=X — Aggregate stats
- GET /api/health/workers — Subsystem health

Optimized queries with select_related to avoid N+1.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional
from datetime import datetime, timedelta
from statistics import mean, stdev

from fastapi import APIRouter, HTTPException, Depends, status, Request, Path, Query
from pydantic import BaseModel, Field, ConfigDict
from tortoise.expressions import Q

from db.models.scope import Project
from db.models.worker import WorkerSession, WorkerState, WorkerStateTransition, WorkerAuditLog

logger = logging.getLogger(__name__)
router = APIRouter(tags=["worker-metrics"])


# ============================================================================
# Request/Response Models
# ============================================================================

class WorkerMetrics(BaseModel):
    """Metrics for a single worker."""
    
    worker_id: str
    step_count: int
    success_rate: float  # 0.0 to 1.0
    avg_duration_ms: float
    current_state: str
    uptime_ms: int


class WorkerAuditEntry(BaseModel):
    """Single audit log entry."""
    
    action: str
    status: str
    user_id: Optional[str]
    scope_level: str
    occurred_at: datetime
    details: dict[str, Any] = Field(default_factory=dict)


class WorkerAuditTrail(BaseModel):
    """Worker audit trail response."""
    
    worker_id: str
    items: list[WorkerAuditEntry]
    total: int
    page: int
    size: int
    has_more: bool


class WorkerSummary(BaseModel):
    """Summary statistics for workers."""
    
    project_id: int
    total_workers: int
    running: int
    paused: int
    completed: int
    failed: int
    queued: int
    avg_step_count: float
    avg_success_rate: float


class HealthStatus(BaseModel):
    """Health status response."""
    
    status: str  # healthy, degraded, unhealthy
    total_workers: int
    avg_metrics: dict[str, Any] = Field(default_factory=dict)
    error_rate: float
    last_error: Optional[str] = None
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str
    message: str
    request_id: str
    scope_level: Optional[str] = None
    resource: Optional[str] = None


# ============================================================================
# Dependency Functions
# ============================================================================

async def get_scope_context(request: Request) -> Any:
    """Extract scope context from request."""
    if not hasattr(request.state, "scope_context"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing scope context"
        )
    return request.state.scope_context


async def validate_scope_access(
    scope: Any = Depends(get_scope_context)
) -> Any:
    """Validate user has access at required scope level."""
    if not scope or not scope.project_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Project scope required"
        )
    return scope


# ============================================================================
# Metrics Endpoints
# ============================================================================

@router.get(
    "/api/workers/{worker_id}/metrics",
    response_model=WorkerMetrics,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        404: {"model": ErrorResponse, "description": "Worker not found"},
    }
)
async def get_worker_metrics(
    worker_id: str = Path(..., description="Worker ID"),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerMetrics:
    """
    Get current metrics for a worker.
    
    Args:
        worker_id: Worker ID
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Worker metrics
    """
    try:
        # Get worker
        worker = await WorkerSession.get_or_none(
            worker_id=worker_id,
            project_id=scope.project_id
        )
        
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worker not found"
            )
        
        # Calculate metrics
        history = worker.execution_history or []
        successful_steps = len([
            h for h in history
            if h.get("status") == "success"
        ])
        success_rate = (
            successful_steps / len(history)
            if history
            else 0.0
        )
        
        # Calculate average duration
        durations = []
        for h in history:
            result = h.get("result", {})
            if isinstance(result, dict) and "duration_ms" in result:
                durations.append(result["duration_ms"])
        
        avg_duration_ms = mean(durations) if durations else 0.0
        
        # Calculate uptime
        uptime_ms = int(
            (datetime.utcnow() - worker.start_time).total_seconds() * 1000
        )
        
        logger.info(
            f"Retrieved metrics for worker {worker_id}",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerMetrics(
            worker_id=worker_id,
            step_count=worker.steps_executed,
            success_rate=success_rate,
            avg_duration_ms=avg_duration_ms,
            current_state=str(worker.current_state),
            uptime_ms=uptime_ms
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving metrics: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/api/workers/{worker_id}/audit",
    response_model=WorkerAuditTrail,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        404: {"model": ErrorResponse, "description": "Worker not found"},
    }
)
async def get_worker_audit(
    worker_id: str = Path(..., description="Worker ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    action: Optional[str] = Query(None, description="Filter by action"),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerAuditTrail:
    """
    Get audit trail for a worker.
    
    Args:
        worker_id: Worker ID
        page: Page number
        size: Page size
        action: Filter by action
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Paginated audit trail
    """
    try:
        # Verify worker exists
        worker = await WorkerSession.get_or_none(
            worker_id=worker_id,
            project_id=scope.project_id
        )
        
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worker not found"
            )
        
        # Build query with select_related
        query = WorkerAuditLog.filter(
            worker_id=worker_id,
            project_id=scope.project_id
        )
        
        if action:
            query = query.filter(action=action)
        
        # Get total count
        total = await query.clone().count()
        
        # Get paginated results
        offset = (page - 1) * size
        audit_logs = await query.select_related(
            "project", "session"
        ).offset(offset).limit(size).order_by(
            "-occurred_at"
        )
        
        has_more = (offset + size) < total
        
        # Convert to response models
        items = [
            WorkerAuditEntry(
                action=log.action,
                status=log.status,
                user_id=log.details.get("user_id") if log.details else None,
                scope_level=log.scope_level,
                occurred_at=log.occurred_at,
                details=log.details or {}
            )
            for log in audit_logs
        ]
        
        logger.info(
            f"Retrieved audit trail for worker {worker_id} ({len(items)} items)",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerAuditTrail(
            worker_id=worker_id,
            items=items,
            total=total,
            page=page,
            size=size,
            has_more=has_more
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving audit trail: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/api/workers/summary",
    response_model=WorkerSummary,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
    }
)
async def get_workers_summary(
    project_id: Optional[int] = Query(None, description="Project ID"),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerSummary:
    """
    Get aggregate statistics for workers in a project.
    
    Args:
        project_id: Project ID (defaults to scope project)
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Worker summary statistics
    """
    try:
        # Use project from scope if not specified
        query_project_id = project_id or scope.project_id
        if not query_project_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project scope required"
            )
        
        # Verify project accessibility
        project = await Project.get_or_none(id=query_project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project not accessible"
            )
        
        # Get all workers with select_related to avoid N+1
        workers = await WorkerSession.filter(
            project_id=query_project_id
        ).select_related("project", "session")
        
        # Calculate statistics
        state_counts = {
            "total": len(workers),
            "running": len([w for w in workers if w.current_state == WorkerState.RUNNING]),
            "paused": len([w for w in workers if w.current_state == WorkerState.PAUSED]),
            "completed": len([w for w in workers if w.current_state == WorkerState.COMPLETED]),
            "failed": len([w for w in workers if w.current_state == WorkerState.FAILED]),
            "queued": len([w for w in workers if w.current_state == WorkerState.QUEUED]),
        }
        
        # Calculate averages
        step_counts = [w.steps_executed for w in workers]
        success_rates = []
        for w in workers:
            history = w.execution_history or []
            if history:
                successful = len([h for h in history if h.get("status") == "success"])
                success_rates.append(successful / len(history))
        
        avg_step_count = mean(step_counts) if step_counts else 0.0
        avg_success_rate = mean(success_rates) if success_rates else 0.0
        
        logger.info(
            f"Retrieved summary for {state_counts['total']} workers in project {query_project_id}",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerSummary(
            project_id=query_project_id,
            total_workers=state_counts["total"],
            running=state_counts["running"],
            paused=state_counts["paused"],
            completed=state_counts["completed"],
            failed=state_counts["failed"],
            queued=state_counts["queued"],
            avg_step_count=avg_step_count,
            avg_success_rate=avg_success_rate
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving summary: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/api/health/workers",
    response_model=HealthStatus
)
async def get_workers_health() -> HealthStatus:
    """
    Get health status of worker subsystem.
    
    Returns:
        Health status
    """
    try:
        # Get all workers
        all_workers = await WorkerSession.all()
        
        if not all_workers:
            return HealthStatus(
                status="healthy",
                total_workers=0,
                avg_metrics={},
                error_rate=0.0,
                timestamp=datetime.utcnow()
            )
        
        # Calculate metrics
        total = len(all_workers)
        
        # Get recent audit logs
        recent_logs = await WorkerAuditLog.filter(
            occurred_at__gte=datetime.utcnow() - timedelta(hours=1)
        ).limit(1000)
        
        failures = len([l for l in recent_logs if l.status == "failure"])
        total_recent = len(recent_logs)
        error_rate = (failures / total_recent) if total_recent > 0 else 0.0
        
        # Calculate average metrics
        step_counts = [w.steps_executed for w in all_workers]
        uptimes = [
            (datetime.utcnow() - w.start_time).total_seconds() * 1000
            for w in all_workers
        ]
        
        avg_metrics = {
            "avg_steps": mean(step_counts) if step_counts else 0,
            "avg_uptime_ms": mean(uptimes) if uptimes else 0,
            "total_workers": total,
        }
        
        # Determine health status
        if error_rate < 0.01:
            status = "healthy"
        elif error_rate < 0.05:
            status = "degraded"
        else:
            status = "unhealthy"
        
        logger.info(
            f"Workers health check: {status} ({error_rate:.1%} error rate)",
            extra={"request_id": "health_check"}
        )
        
        return HealthStatus(
            status=status,
            total_workers=total,
            avg_metrics=avg_metrics,
            error_rate=error_rate,
            last_error=None,
            timestamp=datetime.utcnow()
        )
    
    except Exception as exc:
        logger.error(f"Error checking worker health: {exc}", exc_info=True)
        return HealthStatus(
            status="unhealthy",
            total_workers=0,
            avg_metrics={},
            error_rate=1.0,
            last_error=str(exc),
            timestamp=datetime.utcnow()
        )
