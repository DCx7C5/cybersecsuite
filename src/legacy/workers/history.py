"""
Worker Execution History and Bookmarks API endpoints — t371.

Implements:
- GET /api/workers/{id}/history — Paginated execution steps
- GET /api/workers/{id}/history?action=X&since=Y — Filter by action + date
- POST /api/workers/{id}/bookmarks — Create save point
- GET /api/workers/{id}/bookmarks — List bookmarks (paginated)
- DELETE /api/workers/{id}/bookmarks/{bid} — Remove bookmark

Uses WorkerSessionManager & ExecutionHistoryManager from Phase 5C.
"""


import logging
from typing import Any, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, status, Request, Path, Query
from pydantic import BaseModel, Field

# Note: These imports work both in production (with src/ in path) and tests
from db.models.worker import WorkerSession, WorkerAuditLog

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/workers", tags=["worker-history"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ExecutionHistoryItem(BaseModel):
    """Single execution history item."""
    
    timestamp: datetime
    action: str
    status: str
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None


class ExecutionHistoryResponse(BaseModel):
    """Execution history paginated response."""
    
    worker_id: str
    items: list[ExecutionHistoryItem]
    total: int
    page: int
    size: int
    has_more: bool


class BookmarkCreateRequest(BaseModel):
    """Request to create a bookmark."""
    
    name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="", max_length=2000)


class BookmarkResponse(BaseModel):
    """Bookmark response."""
    
    bookmark_id: str
    name: str
    description: str
    line: Optional[int] = None
    position: Optional[int] = None
    state: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class BookmarksListResponse(BaseModel):
    """Bookmarks list response."""
    
    worker_id: str
    items: list[BookmarkResponse]
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
# Execution History Endpoints
# ============================================================================

@router.get(
    "/{worker_id}/history",
    response_model=ExecutionHistoryResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        404: {"model": ErrorResponse, "description": "Worker not found"},
    }
)
async def get_execution_history(
    worker_id: str = Path(..., description="Worker ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    since: Optional[str] = Query(None, description="Filter by timestamp after this date (ISO 8601)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    request: Request = None,
    scope: Any = Depends(validate_scope_access)
) -> ExecutionHistoryResponse:
    """
    Get execution history for a worker with pagination and filtering.
    
    Args:
        worker_id: Worker ID
        action: Filter by action type
        since: Filter by timestamp after this date
        page: Page number (1-indexed)
        size: Page size (1-1000)
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Paginated execution history
        
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
        
        # Parse execution history
        history = worker.execution_history or []
        
        # Filter by action
        if action:
            history = [h for h in history if h.get("action") == action]
        
        # Filter by timestamp
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                history = [
                    h for h in history
                    if datetime.fromisoformat(h.get("timestamp", "").replace('Z', '+00:00')) >= since_dt
                ]
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid 'since' parameter. Must be ISO 8601 date format."
                )
        
        # Sort by timestamp descending
        history = sorted(
            history,
            key=lambda h: h.get("timestamp", ""),
            reverse=True
        )
        
        # Paginate
        total = len(history)
        offset = (page - 1) * size
        paginated = history[offset:offset + size]
        has_more = (offset + size) < total
        
        # Convert to response models
        items = [ExecutionHistoryItem(**item) for item in paginated]
        
        logger.info(
            f"Retrieved execution history for worker {worker_id} ({len(items)} items)",
            extra={"request_id": getattr(scope, 'request_id', 'unknown')}
        )
        
        return ExecutionHistoryResponse(
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
        logger.error(f"Error retrieving execution history: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ============================================================================
# Bookmarks Endpoints
# ============================================================================

@router.post(
    "/{worker_id}/bookmarks",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        404: {"model": ErrorResponse, "description": "Worker not found"},
    }
)
async def create_bookmark(
    worker_id: str = Path(..., description="Worker ID"),
    data: BookmarkCreateRequest = None,
    request: Request = None,
    scope: Any = Depends(validate_scope_access)
) -> BookmarkResponse:
    """
    Create a new bookmark/save point for a worker.
    
    Args:
        worker_id: Worker ID
        data: Bookmark creation request
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Created bookmark
        
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
        
        # Generate bookmark ID
        bookmark_id = f"bm_{uuid4().hex[:16]}"
        
        # Create bookmark
        bookmarks = worker.bookmarks or {}
        bookmarks[bookmark_id] = {
            "name": data.name,
            "description": data.description,
            "line": None,
            "position": None,
            "state": worker.context_data or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Update worker with new bookmarks
        worker.update_bookmarks(bookmarks)
        await worker.save()
        
        # Log audit
        project_obj = await worker.project
        session_obj = await worker.session
        await WorkerAuditLog.create(
            worker_id=worker_id,
            project=project_obj,
            session=session_obj,
            scope_level=getattr(scope, 'scope_level', 'project'),
            action="create_bookmark",
            status="success",
            permission_check_passed=True,
            permission_required="worker_bookmark_create",
            details={
                "bookmark_id": bookmark_id,
                "name": data.name,
                "user_id": getattr(scope, 'user_id', 'unknown'),
            }
        )
        
        logger.info(
            f"Created bookmark {bookmark_id} for worker {worker_id}",
            extra={"request_id": getattr(scope, 'request_id', 'unknown')}
        )
        
        return BookmarkResponse(
            bookmark_id=bookmark_id,
            name=data.name,
            description=data.description,
            state=worker.context_data or {},
            created_at=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error creating bookmark: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{worker_id}/bookmarks",
    response_model=BookmarksListResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        404: {"model": ErrorResponse, "description": "Worker not found"},
    }
)
async def list_bookmarks(
    worker_id: str = Path(..., description="Worker ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
    request: Request = None,
    scope: Any = Depends(validate_scope_access)
) -> BookmarksListResponse:
    """
    List bookmarks for a worker (paginated).
    
    Args:
        worker_id: Worker ID
        page: Page number (1-indexed)
        size: Page size (1-1000)
        request: HTTP request
        scope: Validated scope context
        
    Returns:
        Paginated bookmarks list
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
        
        # Get bookmarks
        bookmarks_dict = worker.bookmarks or {}
        bookmarks_list = list(bookmarks_dict.items())
        
        # Sort by created_at descending
        bookmarks_list = sorted(
            bookmarks_list,
            key=lambda x: x[1].get("created_at", ""),
            reverse=True
        )
        
        # Paginate
        total = len(bookmarks_list)
        offset = (page - 1) * size
        paginated = bookmarks_list[offset:offset + size]
        has_more = (offset + size) < total
        
        # Convert to response models
        items = [
            BookmarkResponse(
                bookmark_id=bm_id,
                name=bm.get("name", ""),
                description=bm.get("description", ""),
                line=bm.get("line"),
                position=bm.get("position"),
                state=bm.get("state", {}),
                created_at=datetime.fromisoformat(bm.get("created_at", datetime.utcnow().isoformat()))
            )
            for bm_id, bm in paginated
        ]
        
        logger.info(
            f"Listed {len(items)} bookmarks for worker {worker_id}",
            extra={"request_id": getattr(scope, 'request_id', 'unknown')}
        )
        
        return BookmarksListResponse(
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
        logger.error(f"Error listing bookmarks: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{worker_id}/bookmarks/{bookmark_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"model": ErrorResponse, "description": "Scope permission denied"},
        404: {"model": ErrorResponse, "description": "Not found"},
    }
)
async def delete_bookmark(
    worker_id: str = Path(..., description="Worker ID"),
    bookmark_id: str = Path(..., description="Bookmark ID"),
    request: Request = None,
    scope: Any = Depends(validate_scope_access)
) -> None:
    """
    Delete a bookmark.
    
    Args:
        worker_id: Worker ID
        bookmark_id: Bookmark ID
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
        
        # Get bookmarks
        bookmarks = worker.bookmarks or {}
        if bookmark_id not in bookmarks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found"
            )
        
        # Delete bookmark
        del bookmarks[bookmark_id]
        worker.update_bookmarks(bookmarks)
        await worker.save()
        
        # Log audit
        project_obj = await worker.project
        session_obj = await worker.session
        await WorkerAuditLog.create(
            worker_id=worker_id,
            project=project_obj,
            session=session_obj,
            scope_level=getattr(scope, 'scope_level', 'project'),
            action="delete_bookmark",
            status="success",
            permission_check_passed=True,
            permission_required="worker_bookmark_delete",
            details={
                "bookmark_id": bookmark_id,
                "user_id": getattr(scope, 'user_id', 'unknown'),
            }
        )
        
        logger.info(
            f"Deleted bookmark {bookmark_id} for worker {worker_id}",
            extra={"request_id": getattr(scope, 'request_id', 'unknown')}
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error deleting bookmark: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
