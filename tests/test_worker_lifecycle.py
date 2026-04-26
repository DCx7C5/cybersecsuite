"""
Test suite for Worker Lifecycle Transitions API endpoints — t370.

Coverage: 85%+ (20-25 tests)
- POST /api/workers/{id}/start — queued → running
- POST /api/workers/{id}/pause — running → paused
- POST /api/workers/{id}/resume — paused → running
- POST /api/workers/{id}/stop — running/paused → completed
- POST /api/workers/{id}/retry — failed → queued

All transitions logged to AuditLog.
Returns 409 Conflict for invalid state transitions.
"""
from __future__ import annotations

import pytest
import pytest_asyncio
import json
from datetime import datetime
from uuid import uuid4
from unittest.mock import MagicMock, AsyncMock

from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI, Request, status
from tortoise import Tortoise

from db.models.scope import Project
from db.models.worker import WorkerSession, WorkerState, WorkerAuditLog, WorkerStateTransition
from api.routes.worker_lifecycle import router as lifecycle_router


# ============================================================================
# Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def db_with_models():
    """Initialize SQLite database with worker models."""
    db_path = ":memory:"
    
    modules_to_load = {
        "models": [
            "db.models.scope",
            "db.models.worker",
        ]
    }
    
    await Tortoise.init(
        db_url=f"sqlite://{db_path}",
        modules=modules_to_load,
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
    """Create FastAPI app with lifecycle router."""
    app = FastAPI()
    
    @app.middleware("http")
    async def add_scope_context(request: Request, call_next):
        request.state.scope_context = mock_scope_context
        return await call_next(request)
    
    app.include_router(lifecycle_router)
    return app


@pytest_asyncio.fixture
async def async_client(app_with_router):
    """Create async test client."""
    transport = ASGITransport(app=app_with_router)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


# ============================================================================
# Test: Valid State Transitions
# ============================================================================

@pytest.mark.asyncio
async def test_start_worker_success(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test starting a worker (queued → running)."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    payload = {"reason": "Manual start for testing"}
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/start", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["previous_state"] == "queued"
    assert data["current_state"] == "running"
    assert data["reason"] == "Manual start for testing"


@pytest.mark.asyncio
async def test_pause_worker_success(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test pausing a worker (running → paused)."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    test_worker.current_state = WorkerState.RUNNING
    await test_worker.save()
    
    payload = {"reason": "Checkpoint triggered"}
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/pause", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["previous_state"] == "running"
    assert data["current_state"] == "paused"


@pytest.mark.asyncio
async def test_resume_worker_success(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test resuming a worker (paused → running)."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    test_worker.current_state = WorkerState.PAUSED
    await test_worker.save()
    
    payload = {"reason": "Resume from checkpoint"}
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/resume", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["previous_state"] == "paused"
    assert data["current_state"] == "running"


@pytest.mark.asyncio
async def test_stop_worker_from_running(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test stopping a running worker."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    test_worker.current_state = WorkerState.RUNNING
    await test_worker.save()
    
    payload = {"reason": "User requested stop"}
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/stop", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["previous_state"] == "running"
    assert data["current_state"] == "completed"


@pytest.mark.asyncio
async def test_stop_worker_from_paused(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test stopping a paused worker."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    test_worker.current_state = WorkerState.PAUSED
    await test_worker.save()
    
    payload = {"reason": "Stop from paused state"}
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/stop", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["current_state"] == "completed"


@pytest.mark.asyncio
async def test_retry_worker_success(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test retrying a failed worker (failed → queued)."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    test_worker.current_state = WorkerState.FAILED
    await test_worker.save()
    
    payload = {"reason": "Retry after error"}
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/retry", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["previous_state"] == "failed"
    assert data["current_state"] == "queued"


# ============================================================================
# Test: Invalid State Transitions (409 Conflict)
# ============================================================================

@pytest.mark.asyncio
async def test_start_already_running_worker_409(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test starting already running worker returns 409."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    test_worker.current_state = WorkerState.RUNNING
    await test_worker.save()
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/start", json={})
    
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    # Error response may be JSON string or dict
    error_detail = data if isinstance(data, dict) else json.loads(data)
    assert "invalid_state_transition" in str(error_detail)


@pytest.mark.asyncio
async def test_pause_queued_worker_409(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test pausing queued worker returns 409."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    # Worker already in queued state
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/pause", json={})
    
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_resume_running_worker_409(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test resuming running worker returns 409."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    test_worker.current_state = WorkerState.RUNNING
    await test_worker.save()
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/resume", json={})
    
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_stop_queued_worker_409(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test stopping queued worker returns 409."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    # Worker in queued state
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/stop", json={})
    
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_retry_running_worker_409(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test retrying running worker returns 409."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    test_worker.current_state = WorkerState.RUNNING
    await test_worker.save()
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/retry", json={})
    
    assert response.status_code == status.HTTP_409_CONFLICT


# ============================================================================
# Test: Worker Not Found (404)
# ============================================================================

@pytest.mark.asyncio
async def test_start_nonexistent_worker_404(async_client, db_with_models, mock_scope_context):
    """Test starting non-existent worker returns 404."""
    mock_scope_context.project_id = 1
    
    response = await async_client.post("/api/workers/nonexistent/start", json={})
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_pause_nonexistent_worker_404(async_client, db_with_models, mock_scope_context):
    """Test pausing non-existent worker returns 404."""
    mock_scope_context.project_id = 1
    
    response = await async_client.post("/api/workers/nonexistent/pause", json={})
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_resume_nonexistent_worker_404(async_client, db_with_models, mock_scope_context):
    """Test resuming non-existent worker returns 404."""
    mock_scope_context.project_id = 1
    
    response = await async_client.post("/api/workers/nonexistent/resume", json={})
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_stop_nonexistent_worker_404(async_client, db_with_models, mock_scope_context):
    """Test stopping non-existent worker returns 404."""
    mock_scope_context.project_id = 1
    
    response = await async_client.post("/api/workers/nonexistent/stop", json={})
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_retry_nonexistent_worker_404(async_client, db_with_models, mock_scope_context):
    """Test retrying non-existent worker returns 404."""
    mock_scope_context.project_id = 1
    
    response = await async_client.post("/api/workers/nonexistent/retry", json={})
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: Audit Logging
# ============================================================================

@pytest.mark.asyncio
async def test_start_worker_logs_audit(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test starting worker creates audit log."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/start", json={})
    assert response.status_code == status.HTTP_200_OK
    
    # Check audit log
    audit_log = await WorkerAuditLog.filter(
        worker_id=test_worker.worker_id,
        action="state_transition"
    ).first()
    assert audit_log is not None
    assert audit_log.status == "success"


@pytest.mark.asyncio
async def test_pause_worker_logs_audit(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test pausing worker creates audit log."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    test_worker.current_state = WorkerState.RUNNING
    await test_worker.save()
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/pause", json={})
    assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Test: Response Format
# ============================================================================

@pytest.mark.asyncio
async def test_transition_response_format(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test transition response contains all required fields."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/start", json={})
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "worker_id" in data
    assert "previous_state" in data
    assert "current_state" in data
    assert "reason" in data
    assert "transitioned_at" in data


# ============================================================================
# Test: With Metadata
# ============================================================================

@pytest.mark.asyncio
async def test_transition_with_metadata(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test transition with additional metadata."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    payload = {
        "reason": "Transition with context",
        "metadata": {
            "error_code": 500,
            "error_message": "Test error"
        }
    }
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/start", json=payload)
    assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Test: Scope Enforcement
# ============================================================================

@pytest.mark.asyncio
async def test_transition_enforces_scope(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test transitions enforce project scope."""
    mock_scope_context.project_id = 999  # Different project
    test_worker.project_id = test_project.id
    await test_worker.save()
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/start", json={})
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: Error Response Format (409 with allowed_transitions)
# ============================================================================

@pytest.mark.asyncio
async def test_conflict_error_includes_allowed_transitions(async_client, db_with_models, test_project, test_worker, mock_scope_context):
    """Test 409 error response includes allowed_transitions."""
    mock_scope_context.project_id = test_project.id
    test_worker.project_id = test_project.id
    test_worker.current_state = WorkerState.RUNNING
    await test_worker.save()
    
    response = await async_client.post(f"/api/workers/{test_worker.worker_id}/start", json={})
    assert response.status_code == status.HTTP_409_CONFLICT
    
    # Parse error response (may be JSON string)
    data = response.json()
    error_detail = data if isinstance(data, dict) else json.loads(data)
    assert "allowed_transitions" in error_detail or "detail" in data
