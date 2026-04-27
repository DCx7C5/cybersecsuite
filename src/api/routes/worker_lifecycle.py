"""
Worker Lifecycle Transitions API endpoints — t370.

Implements:
- POST /api/workers/{id}/start — queued → running
- POST /api/workers/{id}/pause — running → paused
- POST /api/workers/{id}/resume — paused → running
- POST /api/workers/{id}/stop — running/paused → completed
- POST /api/workers/{id}/retry — failed → queued

Returns 409 Conflict for invalid state transitions.
All transitions logged to AuditLog.
"""
from __future__ import annotations

import logging
import json
from typing import Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Request, Path
from pydantic import BaseModel, Field, ConfigDict

from db.models.scope import ProjectScope
from db.models.worker import WorkerSession, WorkerState
from db.managers.worker_manager import (
    WorkerStateMachine,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/workers", tags=["worker-lifecycle"])


# ============================================================================
# Request/Response Models
# ============================================================================

class TransitionRequest(BaseModel):
    """Request to transition worker state."""
    
    reason: str = Field(default="", max_length=256, description="Transition reason")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional transition context"
    )


class WorkerStateResponse(BaseModel):
    """Response model for worker state."""
    
    worker_id: str
    previous_state: str
    current_state: str
    reason: str
    transitioned_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str
    message: str
    request_id: str
    scope_level: Optional[str] = None
    resource: Optional[str] = None
    current_state: Optional[str] = None
    allowed_transitions: Optional[list[str]] = None


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
# State Transition Endpoints
# ============================================================================

async def _get_worker_for_transition(
    worker_id: str,
    scope: Any
) -> tuple[WorkerSession, ProjectScope]:
    """Get worker and project, validating scope."""
    if not scope.project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project scope required"
        )
    
    worker = await WorkerSession.filter(
        worker_id=worker_id,
        project_id=scope.project_id
    ).select_related("project", "session").first()
    
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found"
        )
    
    project = worker.project
    return worker, project


def _get_valid_transitions(current_state: WorkerState) -> list[str]:
    """Get list of valid transitions from current state."""
    transitions_map = {
        WorkerState.QUEUED: [WorkerState.RUNNING, WorkerState.FAILED],
        WorkerState.RUNNING: [WorkerState.PAUSED, WorkerState.COMPLETED, WorkerState.FAILED],
        WorkerState.PAUSED: [WorkerState.RUNNING, WorkerState.FAILED, WorkerState.COMPLETED],
        WorkerState.COMPLETED: [],
        WorkerState.FAILED: [WorkerState.QUEUED],
    }
    return [str(s) for s in transitions_map.get(current_state, [])]


@router.post(
    "/{worker_id}/start",
    response_model=WorkerStateResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        404: {"model": ErrorResponse, "description": "Worker not found"},
        409: {"model": ErrorResponse, "description": "Invalid state transition"},
    }
)
async def start_worker(
    worker_id: str = Path(..., description="Worker ID"),
    data: TransitionRequest = TransitionRequest(),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerStateResponse:
    """
    Transition worker from queued to running.
    
    Args:
        worker_id: Worker ID
        data: Transition request with reason
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Updated worker state
        
    Raises:
        409: Invalid state transition
    """
    try:
        worker, project = await _get_worker_for_transition(worker_id, scope)
        
        # Verify transition is valid
        if worker.current_state != WorkerState.QUEUED:
            valid_transitions = _get_valid_transitions(worker.current_state)
            error_detail = json.dumps({
                "error": "invalid_state_transition",
                "message": f"Cannot transition from {worker.current_state} to running",
                "request_id": scope.request_id,
                "scope_level": scope.scope_level,
                "current_state": worker.current_state.value,
                "allowed_transitions": valid_transitions,
            })
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_detail
            )
        
        # Execute transition
        state_machine = WorkerStateMachine(
            worker_id=worker_id,
            project_id=scope.project_id,
            session_id=scope.session_id,
            worker_type=worker.worker_type
        )
        
        transition = await state_machine.transition(
            WorkerState.RUNNING,
            reason=data.reason or "manual start",
            metadata=data.metadata
        )
        
        logger.info(
            f"Started worker {worker_id}",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerStateResponse(
            worker_id=worker_id,
            previous_state=transition.from_state.value,
            current_state=transition.to_state.value,
            reason=transition.reason,
            transitioned_at=transition.transitioned_at
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error starting worker: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/{worker_id}/pause",
    response_model=WorkerStateResponse,
    responses={
        409: {"model": ErrorResponse, "description": "Invalid state transition"},
    }
)
async def pause_worker(
    worker_id: str = Path(..., description="Worker ID"),
    data: TransitionRequest = TransitionRequest(),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerStateResponse:
    """
    Transition worker from running to paused.
    
    Args:
        worker_id: Worker ID
        data: Transition request
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Updated worker state
        
    Raises:
        409: Invalid state transition
    """
    try:
        worker, project = await _get_worker_for_transition(worker_id, scope)
        
        # Verify transition is valid
        if worker.current_state != WorkerState.RUNNING:
            valid_transitions = _get_valid_transitions(worker.current_state)
            error_detail = json.dumps({
                "error": "invalid_state_transition",
                "message": f"Cannot transition from {worker.current_state} to paused",
                "request_id": scope.request_id,
                "scope_level": scope.scope_level,
                "current_state": worker.current_state.value,
                "allowed_transitions": valid_transitions,
            })
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_detail
            )
        
        # Execute transition
        state_machine = WorkerStateMachine(
            worker_id=worker_id,
            project_id=scope.project_id,
            session_id=scope.session_id,
            worker_type=worker.worker_type
        )
        
        transition = await state_machine.transition(
            WorkerState.PAUSED,
            reason=data.reason or "manual pause",
            metadata=data.metadata
        )
        
        logger.info(
            f"Paused worker {worker_id}",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerStateResponse(
            worker_id=worker_id,
            previous_state=transition.from_state.value,
            current_state=transition.to_state.value,
            reason=transition.reason,
            transitioned_at=transition.transitioned_at
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error pausing worker: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/{worker_id}/resume",
    response_model=WorkerStateResponse,
    responses={
        409: {"model": ErrorResponse, "description": "Invalid state transition"},
    }
)
async def resume_worker(
    worker_id: str = Path(..., description="Worker ID"),
    data: TransitionRequest = TransitionRequest(),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerStateResponse:
    """
    Transition worker from paused to running.
    
    Args:
        worker_id: Worker ID
        data: Transition request
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Updated worker state
    """
    try:
        worker, project = await _get_worker_for_transition(worker_id, scope)
        
        # Verify transition is valid
        if worker.current_state != WorkerState.PAUSED:
            valid_transitions = _get_valid_transitions(worker.current_state)
            error_detail = json.dumps({
                "error": "invalid_state_transition",
                "message": f"Cannot transition from {worker.current_state} to running",
                "request_id": scope.request_id,
                "scope_level": scope.scope_level,
                "current_state": worker.current_state.value,
                "allowed_transitions": valid_transitions,
            })
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_detail
            )
        
        # Execute transition
        state_machine = WorkerStateMachine(
            worker_id=worker_id,
            project_id=scope.project_id,
            session_id=scope.session_id,
            worker_type=worker.worker_type
        )
        
        transition = await state_machine.transition(
            WorkerState.RUNNING,
            reason=data.reason or "manual resume",
            metadata=data.metadata
        )
        
        logger.info(
            f"Resumed worker {worker_id}",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerStateResponse(
            worker_id=worker_id,
            previous_state=transition.from_state.value,
            current_state=transition.to_state.value,
            reason=transition.reason,
            transitioned_at=transition.transitioned_at
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error resuming worker: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/{worker_id}/stop",
    response_model=WorkerStateResponse,
    responses={
        409: {"model": ErrorResponse, "description": "Invalid state transition"},
    }
)
async def stop_worker(
    worker_id: str = Path(..., description="Worker ID"),
    data: TransitionRequest = TransitionRequest(),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerStateResponse:
    """
    Transition worker from running/paused to completed.
    
    Args:
        worker_id: Worker ID
        data: Transition request
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Updated worker state
    """
    try:
        worker, project = await _get_worker_for_transition(worker_id, scope)
        
        # Verify transition is valid
        if worker.current_state not in [WorkerState.RUNNING, WorkerState.PAUSED]:
            valid_transitions = _get_valid_transitions(worker.current_state)
            error_detail = json.dumps({
                "error": "invalid_state_transition",
                "message": f"Cannot stop worker in {worker.current_state} state",
                "request_id": scope.request_id,
                "scope_level": scope.scope_level,
                "current_state": worker.current_state.value,
                "allowed_transitions": valid_transitions,
            })
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_detail
            )
        
        # Execute transition
        state_machine = WorkerStateMachine(
            worker_id=worker_id,
            project_id=scope.project_id,
            session_id=scope.session_id,
            worker_type=worker.worker_type
        )
        
        transition = await state_machine.transition(
            WorkerState.COMPLETED,
            reason=data.reason or "manual stop",
            metadata=data.metadata
        )
        
        logger.info(
            f"Stopped worker {worker_id}",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerStateResponse(
            worker_id=worker_id,
            previous_state=transition.from_state.value,
            current_state=transition.to_state.value,
            reason=transition.reason,
            transitioned_at=transition.transitioned_at
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error stopping worker: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/{worker_id}/retry",
    response_model=WorkerStateResponse,
    responses={
        409: {"model": ErrorResponse, "description": "Invalid state transition"},
    }
)
async def retry_worker(
    worker_id: str = Path(..., description="Worker ID"),
    data: TransitionRequest = TransitionRequest(),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerStateResponse:
    """
    Retry a failed worker (failed → queued).
    
    Args:
        worker_id: Worker ID
        data: Transition request
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Updated worker state
    """
    try:
        worker, project = await _get_worker_for_transition(worker_id, scope)
        
        # Verify transition is valid
        if worker.current_state != WorkerState.FAILED:
            valid_transitions = _get_valid_transitions(worker.current_state)
            error_detail = json.dumps({
                "error": "invalid_state_transition",
                "message": f"Cannot retry worker in {worker.current_state} state",
                "request_id": scope.request_id,
                "scope_level": scope.scope_level,
                "current_state": worker.current_state.value,
                "allowed_transitions": valid_transitions,
            })
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_detail
            )
        
        # Execute transition
        state_machine = WorkerStateMachine(
            worker_id=worker_id,
            project_id=scope.project_id,
            session_id=scope.session_id,
            worker_type=worker.worker_type
        )
        
        transition = await state_machine.transition(
            WorkerState.QUEUED,
            reason=data.reason or "manual retry",
            metadata=data.metadata
        )
        
        logger.info(
            f"Retried worker {worker_id}",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerStateResponse(
            worker_id=worker_id,
            previous_state=transition.from_state.value,
            current_state=transition.to_state.value,
            reason=transition.reason,
            transitioned_at=transition.transitioned_at
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error retrying worker: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
