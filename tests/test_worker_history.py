"""
Test suite for Worker Execution History and Bookmarks API endpoints — t371.

Coverage: 80%+ (20-25 tests)
- GET /api/workers/{id}/history — Paginated execution steps
- GET /api/workers/{id}/history?action=X&since=Y — Filter by action + date
- POST /api/workers/{id}/bookmarks — Create save point
- GET /api/workers/{id}/bookmarks — List bookmarks
- DELETE /api/workers/{id}/bookmarks/{bid} — Remove bookmark
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from fastapi import FastAPI, Request, status
from tortoise import Tortoise

from db.models.scope import Project
from db.models.worker import WorkerSession, WorkerState
from api.routes.worker_history import router as history_router


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
        name=f"test_project_{uuid4().hex[:8]}"
    )


@pytest_asyncio.fixture
async def test_worker_with_history(db_with_models, test_project):
    """Create a test worker with execution history."""
    now = datetime.utcnow()
    
    history = [
        {
            "timestamp": (now - timedelta(hours=2)).isoformat(),
            "action": "step_completed",
            "status": "success",
            "result": {"duration_ms": 100}
        },
        {
            "timestamp": (now - timedelta(hours=1)).isoformat(),
            "action": "step_completed",
            "status": "success",
            "result": {"duration_ms": 150}
        },
        {
            "timestamp": (now - timedelta(minutes=30)).isoformat(),
            "action": "step_failed",
            "status": "failure",
            "error_message": "Connection timeout"
        },
        {
            "timestamp": now.isoformat(),
            "action": "step_completed",
            "status": "success",
            "result": {"duration_ms": 120}
        },
    ]
    
    worker = await WorkerSession.create(
        worker_id=f"worker_{uuid4().hex[:16]}",
        worker_type="generic",
        project=test_project,
        current_state=WorkerState.RUNNING,
        context_data={"config": {}},
        execution_history=history,
        steps_executed=4
    )
    
    # Update history hashes for integrity
    worker.update_execution_history(history)
    await worker.save()
    
    return worker


@pytest.fixture
def mock_scope_context():
    """Create a mock scope context."""
    ctx = MagicMock()
    ctx.request_id = "req-test-123"
    ctx.scope_level = "project"
    ctx.project_id = 1
    ctx.session_id = None
    ctx.user_id = "user-123"
    return ctx


@pytest.fixture
def app_with_router(mock_scope_context):
    """Create FastAPI app with history router."""
    app = FastAPI()
    
    @app.middleware("http")
    async def add_scope_context(request: Request, call_next):
        request.state.scope_context = mock_scope_context
        return await call_next(request)
    
    app.include_router(history_router)
    return app


@pytest.fixture
def client(app_with_router):
    """Create test client."""
    return TestClient(app_with_router)


# ============================================================================
# Test: GET /api/workers/{id}/history — Execution History
# ============================================================================

@pytest.mark.asyncio
async def test_get_execution_history_success(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test getting execution history successfully."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    response = client.get(f"/api/workers/{test_worker_with_history.worker_id}/history")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 4
    assert data["page"] == 1
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_get_execution_history_pagination(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test execution history pagination."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    response = client.get(f"/api/workers/{test_worker_with_history.worker_id}/history?page=1&size=2")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 2
    assert data["has_more"] is True
    
    # Check second page
    response = client.get(f"/api/workers/{test_worker_with_history.worker_id}/history?page=2&size=2")
    data = response.json()
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_execution_history_filter_by_action(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test filtering execution history by action."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    response = client.get(f"/api/workers/{test_worker_with_history.worker_id}/history?action=step_completed")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    for item in data["items"]:
        assert item["action"] == "step_completed"


@pytest.mark.asyncio
async def test_get_execution_history_filter_by_timestamp(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test filtering execution history by timestamp."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    # Get items from last hour only
    cutoff = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    response = client.get(f"/api/workers/{test_worker_with_history.worker_id}/history?since={cutoff}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2  # Two items from last hour


@pytest.mark.asyncio
async def test_get_execution_history_not_found(client, mock_scope_context):
    """Test getting history for non-existent worker."""
    mock_scope_context.project_id = 1
    
    response = client.get("/api/workers/nonexistent/history")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: POST /api/workers/{id}/bookmarks — Create Bookmark
# ============================================================================

@pytest.mark.asyncio
async def test_create_bookmark_success(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test creating a bookmark successfully."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    payload = {
        "name": "test_bookmark",
        "description": "Test bookmark for unit tests"
    }
    
    response = client.post(
        f"/api/workers/{test_worker_with_history.worker_id}/bookmarks",
        json=payload
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "test_bookmark"
    assert data["description"] == "Test bookmark for unit tests"
    assert "bookmark_id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_multiple_bookmarks(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test creating multiple bookmarks."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    bookmark_ids = []
    for i in range(3):
        payload = {
            "name": f"bookmark_{i}",
            "description": f"Bookmark {i}"
        }
        response = client.post(
            f"/api/workers/{test_worker_with_history.worker_id}/bookmarks",
            json=payload
        )
        assert response.status_code == status.HTTP_201_CREATED
        bookmark_ids.append(response.json()["bookmark_id"])
    
    assert len(bookmark_ids) == 3
    assert len(set(bookmark_ids)) == 3  # All unique


@pytest.mark.asyncio
async def test_create_bookmark_missing_name(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test bookmark creation without name fails."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    payload = {"description": "Missing name"}
    
    response = client.post(
        f"/api/workers/{test_worker_with_history.worker_id}/bookmarks",
        json=payload
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_bookmark_worker_not_found(client, mock_scope_context):
    """Test bookmark creation for non-existent worker."""
    mock_scope_context.project_id = 1
    
    payload = {"name": "test"}
    response = client.post(
        "/api/workers/nonexistent/bookmarks",
        json=payload
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: GET /api/workers/{id}/bookmarks — List Bookmarks
# ============================================================================

@pytest.mark.asyncio
async def test_list_bookmarks_empty(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test listing bookmarks when none exist."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    response = client.get(f"/api/workers/{test_worker_with_history.worker_id}/bookmarks")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_list_bookmarks_success(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test listing bookmarks successfully."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    # Create some bookmarks
    bookmark_ids = []
    for i in range(3):
        payload = {"name": f"bookmark_{i}", "description": f"Desc {i}"}
        response = client.post(
            f"/api/workers/{test_worker_with_history.worker_id}/bookmarks",
            json=payload
        )
        bookmark_ids.append(response.json()["bookmark_id"])
    
    # List bookmarks
    response = client.get(f"/api/workers/{test_worker_with_history.worker_id}/bookmarks")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    
    # Verify all bookmarks are present
    returned_ids = [item["bookmark_id"] for item in data["items"]]
    assert set(returned_ids) == set(bookmark_ids)


@pytest.mark.asyncio
async def test_list_bookmarks_pagination(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test bookmarks list pagination."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    # Create 10 bookmarks
    for i in range(10):
        payload = {"name": f"bookmark_{i}"}
        client.post(
            f"/api/workers/{test_worker_with_history.worker_id}/bookmarks",
            json=payload
        )
    
    # Get first page
    response = client.get(f"/api/workers/{test_worker_with_history.worker_id}/bookmarks?page=1&size=3")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 10
    assert len(data["items"]) == 3
    assert data["has_more"] is True


@pytest.mark.asyncio
async def test_list_bookmarks_not_found(client, mock_scope_context):
    """Test listing bookmarks for non-existent worker."""
    mock_scope_context.project_id = 1
    
    response = client.get("/api/workers/nonexistent/bookmarks")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: DELETE /api/workers/{id}/bookmarks/{bid} — Delete Bookmark
# ============================================================================

@pytest.mark.asyncio
async def test_delete_bookmark_success(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test deleting a bookmark successfully."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    # Create a bookmark
    create_response = client.post(
        f"/api/workers/{test_worker_with_history.worker_id}/bookmarks",
        json={"name": "to_delete"}
    )
    bookmark_id = create_response.json()["bookmark_id"]
    
    # Delete it
    response = client.delete(
        f"/api/workers/{test_worker_with_history.worker_id}/bookmarks/{bookmark_id}"
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's gone
    list_response = client.get(
        f"/api/workers/{test_worker_with_history.worker_id}/bookmarks"
    )
    assert list_response.json()["total"] == 0


@pytest.mark.asyncio
async def test_delete_bookmark_not_found(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test deleting non-existent bookmark."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    response = client.delete(
        f"/api/workers/{test_worker_with_history.worker_id}/bookmarks/nonexistent_bm"
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_bookmark_worker_not_found(client, mock_scope_context):
    """Test deleting bookmark from non-existent worker."""
    mock_scope_context.project_id = 1
    
    response = client.delete(
        "/api/workers/nonexistent/bookmarks/some_bm"
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: Scope Enforcement
# ============================================================================

@pytest.mark.asyncio
async def test_history_enforces_scope(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test history endpoints enforce scope."""
    mock_scope_context.project_id = 999  # Different project
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    response = client.get(f"/api/workers/{test_worker_with_history.worker_id}/history")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_bookmarks_enforce_scope(client, db_with_models, test_project, test_worker_with_history, mock_scope_context):
    """Test bookmarks endpoints enforce scope."""
    mock_scope_context.project_id = 999  # Different project
    test_worker_with_history.project_id = test_project.id
    await test_worker_with_history.save()
    
    response = client.get(f"/api/workers/{test_worker_with_history.worker_id}/bookmarks")
    assert response.status_code == status.HTTP_404_NOT_FOUND
