"""
Worker Batch Operations API endpoints — t373.

Implements bulk operation endpoints for convenience:
- POST /api/workers/batch/start — Start multiple workers
- POST /api/workers/batch/stop — Stop multiple workers
- PATCH /api/workers/batch/update — Update config for multiple workers

Features:
- Atomic per worker (one failure doesn't block others)
- Return results for each worker (success/failure)
- No distributed transactions (each worker transition independent)
- Process up to 100 workers per request
- Scope enforcement (all workers must be in same project)
- Comprehensive audit logging
"""
from __future__ import annotations

import logging
from typing import Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, Field

from db.managers.worker_manager import InvalidStateTransitionError, WorkerStateMachine
from db.models.scope import ProjectScope
from db.models.worker import WorkerSession, WorkerState, WorkerAuditLog

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/workers/batch", tags=["worker-batch"])


# ============================================================================
# Request/Response Models (Pydantic v2)
# ============================================================================

class WorkerConfigUpdate(BaseModel):
    """Partial worker configuration update."""
    
    timeout_seconds: Optional[int] = Field(None, ge=1, le=86400)
    retry_count: Optional[int] = Field(None, ge=0, le=10)
    priority: Optional[int] = Field(None, ge=1, le=10)


class BatchStartRequest(BaseModel):
    """Request to start multiple workers."""
    
    worker_ids: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Worker IDs to start"
    )
    reason: str = Field(
        default="",
        max_length=256,
        description="Reason for batch start"
    )


class BatchStopRequest(BaseModel):
    """Request to stop multiple workers."""
    
    worker_ids: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Worker IDs to stop"
    )
    reason: str = Field(
        default="",
        max_length=256,
        description="Reason for batch stop"
    )


class BatchUpdateRequest(BaseModel):
    """Request to update config for multiple workers."""
    
    worker_ids: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Worker IDs to update"
    )
    config: WorkerConfigUpdate = Field(
        ...,
        description="Configuration fields to update (partial)"
    )


class BatchOperationResult(BaseModel):
    """Result for single worker operation."""
    
    worker_id: str
    status: str = Field(..., pattern="^(success|error)$")
    message: str
    previous_state: Optional[str] = None
    current_state: Optional[str] = None
    updated_fields: Optional[list[str]] = None


class BatchOperationResponse(BaseModel):
    """Response for batch operation."""
    
    results: list[BatchOperationResult]
    total_workers: int
    successful_workers: int
    failed_workers: int
    batch_id: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str
    message: str
    request_id: str
    scope_level: Optional[str] = None


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
    """Validate user has access at project scope level."""
    if not scope or not scope.project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project scope required"
        )
    return scope


# ============================================================================
# Batch Operation Handler
# ============================================================================

async def _process_batch_operation(
    worker_ids: list[str],
    operation: str,
    scope: Any,
    reason: str = "",
    config_update: Optional[WorkerConfigUpdate] = None,
) -> tuple[list[BatchOperationResult], str]:
    """
    Process batch operation for multiple workers.
    
    Atomic per worker (failures don't cascade).
    
    Args:
        worker_ids: List of worker IDs to process
        operation: Operation type (start|stop|update)
        scope: Scope context
        reason: Operation reason
        config_update: Configuration update (for update operation)
        
    Returns:
        Tuple of (results list, batch_id)
    """
    batch_id = f"{operation}_{datetime.utcnow().isoformat()}_{scope.project_id}"
    results: list[BatchOperationResult] = []
    
    # Fetch all workers in one query to avoid N+1
    project_id = scope.project_id
    workers = await WorkerSession.filter(
        worker_id__in=worker_ids,
        project_id=project_id
    ).select_related("project", "session")
    
    # Create lookup map
    worker_map = {w.worker_id: w for w in workers}
    missing_workers = set(worker_ids) - set(worker_map.keys())
    
    # Add errors for missing workers
    for worker_id in missing_workers:
        results.append(BatchOperationResult(
            worker_id=worker_id,
            status="error",
            message="Worker not found in project scope",
            previous_state=None,
            current_state=None,
        ))
    
    # Process each worker
    for worker_id, worker in worker_map.items():
        try:
            previous_state = worker.current_state.value
            
            if operation == "start":
                # Validate transition: queued → running
                if worker.current_state != WorkerState.QUEUED:
                    raise InvalidStateTransitionError(
                        f"Cannot start worker in {worker.current_state} state"
                    )
                
                await state_machine.transition(
                    to_state=WorkerState.RUNNING,
                    reason=reason,
                    metadata={"batch_id": batch_id}
                )
                
                # Refresh worker state
                worker = await WorkerSession.get(worker_id=worker_id)
                current_state = worker.current_state.value
                
                results.append(BatchOperationResult(
                    worker_id=worker_id,
                    status="success",
                    message=f"Worker transitioned from {previous_state} to {current_state}",
                    previous_state=previous_state,
                    current_state=current_state,
                ))
            
            elif operation == "stop":
                # Validate transition: running/paused → completed
                if worker.current_state not in [WorkerState.RUNNING, WorkerState.PAUSED]:
                    raise InvalidStateTransitionError(
                        f"Cannot stop worker in {worker.current_state} state"
                    )
                
                state_machine = WorkerStateMachine(
                    worker_id=worker_id,
                    project_id=project_id,
                    session_id=scope.session_id,
                    worker_type=worker.worker_type
                )
                await state_machine.transition(
                    to_state=WorkerState.COMPLETED,
                    reason=reason,
                    metadata={"batch_id": batch_id}
                )
                
                # Refresh worker state
                worker = await WorkerSession.get(worker_id=worker_id)
                current_state = worker.current_state.value
                
                results.append(BatchOperationResult(
                    worker_id=worker_id,
                    status="success",
                    message=f"Worker transitioned from {previous_state} to {current_state}",
                    previous_state=previous_state,
                    current_state=current_state,
                ))
            
            elif operation == "update":
                # Update configuration (partial)
                if not config_update:
                    raise ValueError("Config update required for update operation")
                
                updated_fields = []
                
                # Build update data from provided fields
                if config_update.timeout_seconds is not None:
                    current_config = worker.context_data.get("config", {})
                    current_config["timeout_seconds"] = config_update.timeout_seconds
                    worker.context_data["config"] = current_config
                    updated_fields.append("timeout_seconds")
                
                if config_update.retry_count is not None:
                    current_config = worker.context_data.get("config", {})
                    current_config["retry_count"] = config_update.retry_count
                    worker.context_data["config"] = current_config
                    updated_fields.append("retry_count")
                
                if config_update.priority is not None:
                    current_config = worker.context_data.get("config", {})
                    current_config["priority"] = config_update.priority
                    worker.context_data["config"] = current_config
                    updated_fields.append("priority")
                
                # Save worker with updated config
                if updated_fields:
                    worker.update_context(worker.context_data)
                    await worker.save()
                
                # Log audit trail
                project = await ProjectScope.get(id=project_id)
                await WorkerAuditLog.create(
                    worker_id=worker_id,
                    project=project,
                    session=worker.session,
                    scope_level="session" if scope.session_id else "project",
                    action="batch_update",
                    status="success",
                    permission_check_passed=True,
                    permission_required="worker_config_update",
                    details={
                        "updated_fields": updated_fields,
                        "batch_id": batch_id,
                    },
                )
                
                results.append(BatchOperationResult(
                    worker_id=worker_id,
                    status="success",
                    message=f"Updated fields: {', '.join(updated_fields)}",
                    updated_fields=updated_fields,
                ))
        
        except InvalidStateTransitionError as e:
            logger.warning(f"Batch operation {operation} failed for {worker_id}: {e}")
            results.append(BatchOperationResult(
                worker_id=worker_id,
                status="error",
                message=str(e),
                previous_state=worker.current_state.value,
                current_state=worker.current_state.value,
            ))
            
            # Log audit trail for failure
            try:
                project = await ProjectScope.get(id=project_id)
                await WorkerAuditLog.create(
                    worker_id=worker_id,
                    project=project,
                    session=worker.session,
                    scope_level="session" if scope.session_id else "project",
                    action=f"batch_{operation}",
                    status="failure",
                    permission_check_passed=True,
                    permission_required=f"worker_{operation}",
                    details={
                        "error": str(e),
                        "batch_id": batch_id,
                    },
                )
            except Exception as audit_error:
                logger.error(f"Failed to log audit trail: {audit_error}")
        
        except Exception as e:
            logger.error(f"Batch operation {operation} failed for {worker_id}: {e}")
            results.append(BatchOperationResult(
                worker_id=worker_id,
                status="error",
                message=f"Internal error: {str(e)}",
            ))
    
    return results, batch_id


# ============================================================================
# Batch Endpoints
# ============================================================================

@router.post(
    "/start",
    response_model=BatchOperationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        403: {"model": ErrorResponse, "description": "Scope denied"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    }
)
async def batch_start_workers(
    data: BatchStartRequest,
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> BatchOperationResponse:
    """
    Start multiple workers in batch.
    
    Transitions: queued → running
    Atomic per worker (failures don't cascade)
    
    Args:
        data: Batch start request
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Batch operation response with per-worker results
    """
    logger.info(
        f"Batch start requested for {len(data.worker_ids)} workers "
        f"in project {scope.project_id}"
    )
    
    results, batch_id = await _process_batch_operation(
        worker_ids=data.worker_ids,
        operation="start",
        scope=scope,
        reason=data.reason,
    )
    
    successful = sum(1 for r in results if r.status == "success")
    failed = sum(1 for r in results if r.status == "error")
    
    logger.info(
        f"Batch start completed: {successful} successful, {failed} failed "
        f"(batch_id: {batch_id})"
    )
    
    return BatchOperationResponse(
        results=results,
        total_workers=len(data.worker_ids),
        successful_workers=successful,
        failed_workers=failed,
        batch_id=batch_id,
    )


@router.post(
    "/stop",
    response_model=BatchOperationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        403: {"model": ErrorResponse, "description": "Scope denied"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    }
)
async def batch_stop_workers(
    data: BatchStopRequest,
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> BatchOperationResponse:
    """
    Stop multiple workers in batch.
    
    Transitions: running/paused → completed
    Atomic per worker (failures don't cascade)
    
    Args:
        data: Batch stop request
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Batch operation response with per-worker results
    """
    logger.info(
        f"Batch stop requested for {len(data.worker_ids)} workers "
        f"in project {scope.project_id}"
    )
    
    results, batch_id = await _process_batch_operation(
        worker_ids=data.worker_ids,
        operation="stop",
        scope=scope,
        reason=data.reason,
    )
    
    successful = sum(1 for r in results if r.status == "success")
    failed = sum(1 for r in results if r.status == "error")
    
    logger.info(
        f"Batch stop completed: {successful} successful, {failed} failed "
        f"(batch_id: {batch_id})"
    )
    
    return BatchOperationResponse(
        results=results,
        total_workers=len(data.worker_ids),
        successful_workers=successful,
        failed_workers=failed,
        batch_id=batch_id,
    )


@router.patch(
    "/update",
    response_model=BatchOperationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        403: {"model": ErrorResponse, "description": "Scope denied"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    }
)
async def batch_update_workers(
    data: BatchUpdateRequest,
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> BatchOperationResponse:
    """
    Update configuration for multiple workers in batch.
    
    Supports partial field updates
    Atomic per worker (failures don't cascade)
    
    Args:
        data: Batch update request
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Batch operation response with per-worker results
    """
    logger.info(
        f"Batch update requested for {len(data.worker_ids)} workers "
        f"in project {scope.project_id}"
    )
    
    results, batch_id = await _process_batch_operation(
        worker_ids=data.worker_ids,
        operation="update",
        scope=scope,
        config_update=data.config,
    )
    
    successful = sum(1 for r in results if r.status == "success")
    failed = sum(1 for r in results if r.status == "error")
    
    logger.info(
        f"Batch update completed: {successful} successful, {failed} failed "
        f"(batch_id: {batch_id})"
    )
    
    return BatchOperationResponse(
        results=results,
        total_workers=len(data.worker_ids),
        successful_workers=successful,
        failed_workers=failed,
        batch_id=batch_id,
    )
