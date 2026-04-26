"""
Test suite for Worker CRUD API endpoints — t369.

Coverage: 85%+ (25-35 tests)
- POST /api/workers — Create worker with validation
- GET /api/workers — List with pagination and filtering
- GET /api/workers/{id} — Get single worker
- PATCH /api/workers/{id} — Update worker config
- DELETE /api/workers/{id} — Soft delete worker
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4

from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI, Request, status
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from db.models.scope import Project, Session
from db.models.worker import WorkerSession, WorkerState, WorkerAuditLog
from api.routes.workers import router as workers_router


# ============================================================================
# Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def db_with_models():
    """Initialize SQLite database with worker models."""
    db_path = ":memory:"
    
    modules_to_load = [
        "db.models.scope",
        "db.models.worker",
    ]
    
    await Tortoise.init(
        db_url=f"sqlite://{db_path}",
        modules={"models": modules_to_load},
    )
    await Tortoise.generate_schemas()
    yield Tortoise
    await Tortoise.close_connections()


@pytest_asyncio.fixture
async def test_project(db_with_models):
    """Create a test project."""
    return await Project.create(
        name=f"test_project_{uuid4().hex[:8]}",
        description="Test project"
    )


@pytest_asyncio.fixture
async def test_session(db_with_models, test_project):
    """Create a test session."""
    return await Session.create(
        session_id=f"sess_{uuid4().hex[:8]}",
        project=test_project,
        status="active"
    )


@pytest_asyncio.fixture
async def test_worker(db_with_models, test_project):
    """Create a test worker."""
    return await WorkerSession.create(
        worker_id=f"worker_{uuid4().hex[:16]}",
        worker_type="generic",
        project=test_project,
        current_state=WorkerState.QUEUED,
        context_data={"config": {}}
    )


@pytest_asyncio.fixture
async def mock_scope_context():
    """Create a mock scope context."""
    ctx = MagicMock()
    ctx.request_id = "req-test-123"
    ctx.scope_level = "project"
    ctx.project_id = 1
    ctx.session_id = None
    ctx.user_id = "user-123"
    return ctx


@pytest_asyncio.fixture
async def app_with_router(mock_scope_context):
    """Create FastAPI app with workers router."""
    app = FastAPI()
    
    @app.middleware("http")
    async def add_scope_context(request: Request, call_next):
        request.state.scope_context = mock_scope_context
        return await call_next(request)
    
    app.include_router(workers_router)
    return app


@pytest_asyncio.fixture
async def async_client(app_with_router):
    """Create async test client."""
    transport = ASGITransport(app=app_with_router)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


# ============================================================================
# Test: POST /api/workers — Create Worker
# ============================================================================

@pytest.mark.asyncio
async def test_create_worker_success(async_client, db_with_models, mock_scope_context, test_project):
    """Test successful worker creation."""
    mock_scope_context.project_id = test_project.id
    
    payload = {
        "name": "test_worker",
        "description": "Test worker for unit tests",
        "worker_type": "generic",
        "config": {
            "params": {"key": "value"},
            "timeout_seconds": 3600,
            "retry_count": 2,
            "priority": 5
        }
    }
    
    response = await async_client.post("/api/workers/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["worker_type"] == "generic"
    assert data["current_state"] == "queued"


@pytest.mark.asyncio
async def test_create_worker_invalid_name(async_client):
    """Test worker creation with invalid name."""
    payload = {
        "name": "test@worker!",  # Invalid characters
        "description": "Test",
        "worker_type": "generic",
        "config": {}
    }
    
    response = await async_client.post("/api/workers/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_worker_missing_name(async_client):
    """Test worker creation without name."""
    payload = {
        "description": "Test",
        "worker_type": "generic",
        "config": {}
    }
    
    response = await async_client.post("/api/workers/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_worker_no_scope(async_client, mock_scope_context):
    """Test worker creation without scope."""
    # Remove project_id to simulate no scope
    mock_scope_context.project_id = None
    
    payload = {
        "name": "test_worker",
        "description": "Test",
        "worker_type": "generic",
        "config": {}
    }
    
    response = await async_client.post("/api/workers/", json=payload)
    # Should fail due to missing scope
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# Test: GET /api/workers — List Workers
# ============================================================================

@pytest.mark.asyncio
async def test_list_workers_success(async_client, db_with_models, test_project, mock_scope_context):
    """Test listing workers successfully."""
    # Create test workers
    mock_scope_context.project_id = test_project.id
    
    for i in range(5):
        await WorkerSession.create(
            worker_id=f"worker_{uuid4().hex[:16]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.QUEUED,
        )
    
    response = await async_client.get("/api/workers/")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5
    assert data["page"] == 1
    assert data["size"] == 50
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_list_workers_pagination(async_client, db_with_models, test_project, mock_scope_context):
    """Test workers list pagination."""
    mock_scope_context.project_id = test_project.id
    
    # Create 100 workers
    for i in range(100):
        await WorkerSession.create(
            worker_id=f"worker_{uuid4().hex[:16]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.QUEUED,
        )
    
    # Request first page with size 25
    response = await async_client.get("/api/workers/?page=1&size=25")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 100
    assert len(data["items"]) == 25
    assert data["page"] == 1
    assert data["has_more"] is True
    
    # Request second page
    response = await async_client.get("/api/workers/?page=2&size=25")
    data = response.json()
    assert len(data["items"]) == 25
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_list_workers_filter_by_state(async_client, db_with_models, test_project, mock_scope_context):
    """Test filtering workers by state."""
    mock_scope_context.project_id = test_project.id
    
    # Create workers in different states
    for i in range(3):
        await WorkerSession.create(
            worker_id=f"worker_{uuid4().hex[:16]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.RUNNING,
        )
    
    for i in range(2):
        await WorkerSession.create(
            worker_id=f"worker_{uuid4().hex[:16]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.QUEUED,
        )
    
    response = await async_client.get("/api/workers/?state=running")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    for item in data["items"]:
        assert item["current_state"] == "running"


@pytest.mark.asyncio
async def test_list_workers_invalid_state_filter(async_client, mock_scope_context, test_project):
    """Test filtering with invalid state."""
    mock_scope_context.project_id = test_project.id
    
    response = await async_client.get("/api/workers/?state=invalid_state")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# Test: GET /api/workers/{id} — Get Single Worker
# ============================================================================

@pytest.mark.asyncio
async def test_get_worker_success(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test getting a single worker successfully."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    response = await async_client.get(f"/api/workers/{test_worker.worker_id}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["worker_id"] == test_worker.worker_id
    assert data["current_state"] == "queued"


@pytest.mark.asyncio
async def test_get_worker_not_found(async_client, mock_scope_context, test_project):
    """Test getting non-existent worker."""
    mock_scope_context.project_id = test_project.id
    
    response = await async_client.get("/api/workers/nonexistent_worker")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_worker_cross_project_access_denied(
    async_client, db_with_models, test_project, test_worker, mock_scope_context
):
    """Test cross-project worker access is denied."""
    # Create another project
    other_project = await Project.create(
        name=f"other_project_{uuid4().hex[:8]}"
    )
    
    test_worker.project_id = other_project.id
    await test_worker.save()
    
    # Try to access from different project scope
    mock_scope_context.project_id = test_project.id
    
    response = await async_client.get(f"/api/workers/{test_worker.worker_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: PATCH /api/workers/{id} — Update Worker
# ============================================================================

@pytest.mark.asyncio
async def test_update_worker_success(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test updating worker successfully."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    payload = {
        "name": "updated_name",
        "description": "Updated description",
        "config": {
            "params": {"new_key": "new_value"},
            "timeout_seconds": 7200,
            "retry_count": 3,
            "priority": 8
        }
    }
    
    response = await async_client.patch(f"/api/workers/{test_worker.worker_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_worker_partial(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test partial worker update."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    payload = {
        "description": "Only updating description"
    }
    
    response = await async_client.patch(f"/api/workers/{test_worker.worker_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["description"] == "Only updating description"


@pytest.mark.asyncio
async def test_update_worker_not_found(async_client, mock_scope_context, test_project):
    """Test updating non-existent worker."""
    mock_scope_context.project_id = test_project.id
    
    response = await async_client.patch("/api/workers/nonexistent", json={"description": "Test"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: DELETE /api/workers/{id} — Delete Worker
# ============================================================================

@pytest.mark.asyncio
async def test_delete_worker_success(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test deleting worker successfully."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    response = await async_client.delete(f"/api/workers/{test_worker.worker_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify worker is gone
    deleted_worker = await WorkerSession.get_or_none(worker_id=test_worker.worker_id)
    assert deleted_worker is None


@pytest.mark.asyncio
async def test_delete_worker_not_found(async_client, mock_scope_context, test_project):
    """Test deleting non-existent worker."""
    mock_scope_context.project_id = test_project.id
    
    response = await async_client.delete("/api/workers/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_worker_logs_audit(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test deleting worker creates audit log."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    response = await async_client.delete(f"/api/workers/{test_worker.worker_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Check audit log
    audit_log = await WorkerAuditLog.filter(
        worker_id=test_worker.worker_id,
        action="delete"
    ).first()
    assert audit_log is not None


# ============================================================================
# Test: Audit Logging
# ============================================================================

@pytest.mark.asyncio
async def test_create_worker_logs_audit(async_client, db_with_models, test_project, mock_scope_context):
    """Test worker creation creates audit log."""
    mock_scope_context.project_id = test_project.id
    
    payload = {
        "name": "audit_test_worker",
        "description": "Testing audit logging",
        "worker_type": "generic",
        "config": {}
    }
    
    response = await async_client.post("/api/workers/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    worker_id = data["worker_id"]
    
    # Check audit log
    audit_log = await WorkerAuditLog.filter(
        worker_id=worker_id,
        action="create"
    ).first()
    assert audit_log is not None
    assert audit_log.status == "success"


@pytest.mark.asyncio
async def test_update_worker_logs_audit(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test worker update creates audit log."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    response = await async_client.patch(
        f"/api/workers/{test_worker.worker_id}",
        json={"description": "Updated for audit test"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Check audit log
    audit_log = await WorkerAuditLog.filter(
        worker_id=test_worker.worker_id,
        action="update"
    ).first()
    assert audit_log is not None


# ============================================================================
# Test: Error Responses
# ============================================================================

@pytest.mark.asyncio
async def test_error_response_format(async_client, mock_scope_context, test_project):
    """Test error response format."""
    mock_scope_context.project_id = test_project.id
    
    response = await async_client.get("/api/workers/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    data = response.json()
    assert "detail" in data


# ============================================================================
# Test: Scope Enforcement
# ============================================================================

@pytest.mark.asyncio
async def test_list_workers_enforces_scope(async_client, db_with_models, test_project, mock_scope_context):
    """Test list workers enforces project scope."""
    mock_scope_context.project_id = None  # No scope
    
    response = await async_client.get("/api/workers/")
    # Should fail or return empty based on implementation
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
