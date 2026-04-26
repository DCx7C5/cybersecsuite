"""
Worker CRUD API endpoints — t369.

Implements:
- POST /api/workers — Create new worker
- GET /api/workers?project_id=X — List + filter (paginated)
- GET /api/workers/{id} — Fetch single worker
- PATCH /api/workers/{id} — Update worker config
- DELETE /api/workers/{id} — Soft delete worker

All endpoints enforce scope via request.state.scope_context
"""
from __future__ import annotations

import logging
import hashlib
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, status, Request, Query, Path
from pydantic import BaseModel, Field, field_validator, ConfigDict
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from db.models.scope import Project, Session
from db.models.worker import WorkerSession, WorkerState, WorkerAuditLog
from db.worker_manager import WorkerStateMachine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/workers", tags=["workers"])


# ============================================================================
# Request/Response Models (Pydantic v2)
# ============================================================================

class WorkerConfigModel(BaseModel):
    """Worker configuration."""
    
    params: dict[str, Any] = Field(default_factory=dict, description="Worker parameters")
    timeout_seconds: int = Field(default=3600, ge=1, le=86400)
    retry_count: int = Field(default=0, ge=0, le=10)
    priority: int = Field(default=5, ge=1, le=10)


class WorkerCreateRequest(BaseModel):
    """Request to create a new worker."""
    
    name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="", max_length=2000)
    worker_type: str = Field(default="generic", max_length=64)
    config: WorkerConfigModel = Field(default_factory=WorkerConfigModel)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate worker name format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Worker name must contain only alphanumeric, dash, underscore")
        return v


class WorkerUpdateRequest(BaseModel):
    """Request to update an existing worker."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    config: Optional[WorkerConfigModel] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate worker name format."""
        if v and not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Worker name must contain only alphanumeric, dash, underscore")
        return v


class WorkerResponse(BaseModel):
    """Response model for worker."""
    
    id: int
    worker_id: str
    name: str
    description: str
    worker_type: str
    current_state: str
    config: dict[str, Any]
    project_id: int
    session_id: Optional[int]
    steps_executed: int
    total_duration_ms: int
    start_time: datetime
    last_activity_at: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedWorkersResponse(BaseModel):
    """Paginated workers response."""
    
    items: list[WorkerResponse]
    total: int
    page: int
    size: int
    has_more: bool


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
    scope: Any = Depends(get_scope_context),
    required_level: str = "project"
) -> Any:
    """Validate user has access at required scope level."""
    if not scope:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    return scope


# ============================================================================
# CRUD Endpoints
# ============================================================================

@router.post(
    "/",
    response_model=WorkerResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    }
)
async def create_worker(
    data: WorkerCreateRequest,
    request: Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerResponse:
    """
    Create a new worker.
    
    Args:
        data: Worker creation request
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Created worker response
        
    Raises:
        403: Scope permission denied
        422: Validation error
    """
    try:
        # Validate scope has project_id
        if not scope.project_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ErrorResponse(
                    error="scope_permission_denied",
                    message="Project scope required",
                    request_id=scope.request_id,
                    scope_level=scope.scope_level
                ).model_dump()
            )
        
        # Get project
        project = await Project.get_or_none(id=scope.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project not accessible"
            )
        
        # Generate worker ID
        worker_id = f"worker_{uuid4().hex[:16]}"
        
        # Create worker session transactionally
        async with in_transaction():
            session_obj = None
            if scope.session_id:
                session_obj = await Session.get_or_none(session_id=scope.session_id)
            
            worker_session = await WorkerSession.create(
                worker_id=worker_id,
                worker_type=data.worker_type,
                project=project,
                session=session_obj,
                current_state=WorkerState.QUEUED,
                context_data={"config": data.config.model_dump()},
            )
            
            # Log audit
            await WorkerAuditLog.create(
                worker_id=worker_id,
                project=project,
                session=session_obj,
                scope_level=scope.scope_level,
                action="create",
                status="success",
                permission_check_passed=True,
                permission_required="worker_create",
                details={
                    "name": data.name,
                    "worker_type": data.worker_type,
                    "user_id": scope.user_id,
                }
            )
        
        logger.info(
            f"Worker created: {worker_id} in project {scope.project_id}",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerResponse.model_validate(worker_session)
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error creating worker: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/",
    response_model=PaginatedWorkersResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
    }
)
async def list_workers(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    state: Optional[str] = Query(None, description="Filter by state"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> PaginatedWorkersResponse:
    """
    List workers with pagination and filtering.
    
    Args:
        project_id: Filter by project ID
        state: Filter by worker state
        page: Page number (1-indexed)
        size: Page size (1-1000)
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Paginated worker list
    """
    try:
        # Enforce scope
        query_project_id = project_id or scope.project_id
        if not query_project_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project scope required"
            )
        
        # Verify project accessibility
        project = await Project.get_or_none(id=query_project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        # Build query with select_related to avoid N+1
        query = WorkerSession.filter(project_id=query_project_id)
        
        if state:
            try:
                state_enum = WorkerState(state)
                query = query.filter(current_state=state_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid state: {state}"
                )
        
        # Get total count
        total = await query.clone().count()
        
        # Get paginated results with select_related
        offset = (page - 1) * size
        workers = await query.select_related(
            "project", "session"
        ).offset(offset).limit(size).order_by(
            "-last_activity_at"
        )
        
        has_more = (offset + size) < total
        
        logger.info(
            f"Listed {len(workers)} workers for project {query_project_id}",
            extra={"request_id": scope.request_id}
        )
        
        return PaginatedWorkersResponse(
            items=[WorkerResponse.model_validate(w) for w in workers],
            total=total,
            page=page,
            size=size,
            has_more=has_more
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error listing workers: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{worker_id}",
    response_model=WorkerResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        404: {"model": ErrorResponse, "description": "Worker not found"},
    }
)
async def get_worker(
    worker_id: str = Path(..., description="Worker ID"),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerResponse:
    """
    Get a specific worker by ID.
    
    Args:
        worker_id: Worker ID
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Worker response
        
    Raises:
        403: Scope permission denied
        404: Worker not found
    """
    try:
        # Enforce scope
        if not scope.project_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project scope required"
            )
        
        # Get worker with select_related
        worker = await WorkerSession.get_or_none(
            worker_id=worker_id,
            project_id=scope.project_id
        ).select_related("project", "session")
        
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worker not found"
            )
        
        logger.info(
            f"Retrieved worker {worker_id}",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerResponse.model_validate(worker)
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error getting worker: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch(
    "/{worker_id}",
    response_model=WorkerResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        404: {"model": ErrorResponse, "description": "Worker not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    }
)
async def update_worker(
    worker_id: str = Path(..., description="Worker ID"),
    data: WorkerUpdateRequest = None,
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> WorkerResponse:
    """
    Update a worker's configuration.
    
    Args:
        worker_id: Worker ID
        data: Update request
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Updated worker response
    """
    try:
        # Enforce scope
        if not scope.project_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project scope required"
            )
        
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
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        if "config" in update_data:
            config_data = update_data.pop("config")
            context = worker.context_data or {}
            context["config"] = config_data.model_dump()
            worker.update_context(context)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(worker, field, value)
        
        await worker.save()
        
        # Log audit
        session_obj = await worker.session
        project_obj = await worker.project
        await WorkerAuditLog.create(
            worker_id=worker_id,
            project=project_obj,
            session=session_obj,
            scope_level=scope.scope_level,
            action="update",
            status="success",
            permission_check_passed=True,
            permission_required="worker_update",
            details={
                "updated_fields": list(update_data.keys()),
                "user_id": scope.user_id,
            }
        )
        
        logger.info(
            f"Updated worker {worker_id}",
            extra={"request_id": scope.request_id}
        )
        
        return WorkerResponse.model_validate(worker)
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error updating worker: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{worker_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        404: {"model": ErrorResponse, "description": "Worker not found"},
    }
)
async def delete_worker(
    worker_id: str = Path(..., description="Worker ID"),
    request: Request = Request,
    scope: Any = Depends(validate_scope_access)
) -> None:
    """
    Soft delete a worker (mark as deleted).
    
    Args:
        worker_id: Worker ID
        request: HTTP request
        scope: Validated scope context
    """
    try:
        # Enforce scope
        if not scope.project_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project scope required"
            )
        
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
        
        # Soft delete
        await worker.delete()
        
        # Log audit
        project_obj = await worker.project
        session_obj = await worker.session
        await WorkerAuditLog.create(
            worker_id=worker_id,
            project=project_obj,
            session=session_obj,
            scope_level=scope.scope_level,
            action="delete",
            status="success",
            permission_check_passed=True,
            permission_required="worker_delete",
            details={
                "user_id": scope.user_id,
                "soft_delete": True,
            }
        )
        
        logger.info(
            f"Deleted worker {worker_id}",
            extra={"request_id": scope.request_id}
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error deleting worker: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
