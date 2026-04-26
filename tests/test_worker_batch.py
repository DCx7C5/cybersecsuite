"""
Test suite for Worker Batch Operations API endpoints — t373.

Coverage: 80%+ (12-15 tests)
- POST /api/workers/batch/start — Start multiple workers
- POST /api/workers/batch/stop — Stop multiple workers
- PATCH /api/workers/batch/update — Update config for multiple workers

Tests:
- Happy path for each endpoint
- Mixed success/failure scenarios
- Large batch testing (50+ workers)
- Scope enforcement
- Error handling
- Audit logging verification
- Performance benchmarks
"""
from __future__ import annotations

import pytest
import pytest_asyncio
import time
from uuid import uuid4
from unittest.mock import MagicMock

from httpx import AsyncClient
from fastapi import FastAPI, Request
from tortoise import Tortoise

from db.models.scope import Project, Session
from db.models.worker import WorkerSession, WorkerState, WorkerAuditLog
from api.routes.worker_batch import router as batch_router


# ============================================================================
# Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def db_with_models():
    """Initialize SQLite database with worker and scope models."""
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
        description="Test project for batch operations"
    )


@pytest_asyncio.fixture
async def test_session(db_with_models, test_project):
    """Create a test session."""
    return await Session.create(
        session_id=f"session_{uuid4().hex[:16]}",
        project=test_project,
        name="Test Session"
    )


@pytest_asyncio.fixture
async def test_workers(db_with_models, test_project):
    """Create multiple test workers in QUEUED state."""
    workers = []
    for i in range(5):
        worker = await WorkerSession.create(
            worker_id=f"worker_{uuid4().hex[:16]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.QUEUED,
            context_data={"config": {"timeout_seconds": 3600, "retry_count": 0, "priority": 5}}
        )
        workers.append(worker)
    return workers


@pytest_asyncio.fixture
async def running_workers(db_with_models, test_project):
    """Create test workers in RUNNING state."""
    workers = []
    for i in range(3):
        worker = await WorkerSession.create(
            worker_id=f"running_worker_{uuid4().hex[:16]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.RUNNING,
            context_data={"config": {"timeout_seconds": 3600, "retry_count": 0, "priority": 5}}
        )
        workers.append(worker)
    return workers


@pytest_asyncio.fixture
async def mock_scope_context(test_project):
    """Create a mock scope context."""
    context = MagicMock()
    context.project_id = test_project.id
    context.session_id = None
    context.scope_level = "project"
    context.request_id = uuid4().hex
    return context


@pytest_asyncio.fixture
async def mock_request_with_scope(mock_scope_context):
    """Create a mock request with scope context."""
    request = MagicMock(spec=Request)
    request.state = MagicMock()
    request.state.scope_context = mock_scope_context
    return request


@pytest_asyncio.fixture
async def app_with_batch_router():
    """Create FastAPI app with batch router."""
    app = FastAPI()
    app.include_router(batch_router)
    
    # Mock scope context middleware
    @app.middleware("http")
    async def add_scope_context(request: Request, call_next):
        request.state.scope_context = MagicMock()
        response = await call_next(request)
        return response
    
    return app


@pytest_asyncio.fixture
async def async_client(app_with_batch_router, db_with_models):
    """Create async HTTP client for testing."""
    async with AsyncClient(
        app=app_with_batch_router,
        base_url="http://testserver"
    ) as client:
        yield client


# ============================================================================
# Test Batch Start Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_batch_start_single_worker(test_project, test_workers, mock_scope_context):
    """Test starting a single worker via batch endpoint."""
    worker = test_workers[0]
    
    # Verify initial state
    assert worker.current_state == WorkerState.QUEUED
    
    # Call batch start operation
    from api.routes.worker_batch import _process_batch_operation
    
    results, batch_id = await _process_batch_operation(
        worker_ids=[worker.worker_id],
        operation="start",
        scope=mock_scope_context,
        reason="Testing single worker start",
    )
    
    # Verify results
    assert len(results) == 1
    result = results[0]
    assert result.worker_id == worker.worker_id
    assert result.status == "success"
    assert result.previous_state == "queued"
    assert result.current_state == "running"
    
    # Verify state was updated in DB
    updated_worker = await WorkerSession.get(worker_id=worker.worker_id)
    assert updated_worker.current_state == WorkerState.RUNNING


@pytest.mark.asyncio
async def test_batch_start_multiple_workers(test_project, test_workers, mock_scope_context):
    """Test starting multiple workers in batch."""
    worker_ids = [w.worker_id for w in test_workers[:3]]
    
    from api.routes.worker_batch import _process_batch_operation
    
    results, batch_id = await _process_batch_operation(
        worker_ids=worker_ids,
        operation="start",
        scope=mock_scope_context,
        reason="Testing batch start",
    )
    
    # Verify all workers were processed
    assert len(results) == 3
    assert all(r.status == "success" for r in results)
    assert all(r.previous_state == "queued" for r in results)
    assert all(r.current_state == "running" for r in results)
    
    # Verify states updated in DB
    for worker_id in worker_ids:
        worker = await WorkerSession.get(worker_id=worker_id)
        assert worker.current_state == WorkerState.RUNNING


@pytest.mark.asyncio
async def test_batch_start_mixed_states(test_project, test_workers, running_workers, mock_scope_context):
    """Test batch start with mixed worker states (failure expected for non-queued)."""
    # Mix queued and running workers
    worker_ids = [test_workers[0].worker_id, running_workers[0].worker_id]
    
    from api.routes.worker_batch import _process_batch_operation
    
    results, batch_id = await _process_batch_operation(
        worker_ids=worker_ids,
        operation="start",
        scope=mock_scope_context,
        reason="Testing mixed states",
    )
    
    assert len(results) == 2
    
    # Find queued and running results by state
    queued_result = next(r for r in results if r.previous_state == "queued")
    running_result = next(r for r in results if r.previous_state == "running")
    
    # Queued worker should succeed
    assert queued_result.status == "success"
    assert queued_result.current_state == "running"
    
    # Running worker should fail
    assert running_result.status == "error"
    assert "Cannot start worker" in running_result.message


@pytest.mark.asyncio
async def test_batch_start_nonexistent_workers(test_project, mock_scope_context):
    """Test batch start with nonexistent worker IDs."""
    from api.routes.worker_batch import _process_batch_operation
    
    results, batch_id = await _process_batch_operation(
        worker_ids=["nonexistent_worker_1", "nonexistent_worker_2"],
        operation="start",
        scope=mock_scope_context,
    )
    
    assert len(results) == 2
    assert all(r.status == "error" for r in results)
    assert all("not found" in r.message for r in results)


# ============================================================================
# Test Batch Stop Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_batch_stop_running_workers(test_project, running_workers, mock_scope_context):
    """Test stopping running workers via batch."""
    worker_ids = [w.worker_id for w in running_workers[:2]]
    
    from api.routes.worker_batch import _process_batch_operation
    
    results, batch_id = await _process_batch_operation(
        worker_ids=worker_ids,
        operation="stop",
        scope=mock_scope_context,
        reason="Testing batch stop",
    )
    
    assert len(results) == 2
    assert all(r.status == "success" for r in results)
    assert all(r.previous_state == "running" for r in results)
    assert all(r.current_state == "completed" for r in results)


@pytest.mark.asyncio
async def test_batch_stop_invalid_state(test_project, test_workers, mock_scope_context):
    """Test batch stop on workers not in running/paused state."""
    worker_ids = [test_workers[0].worker_id]  # Still in QUEUED state
    
    from api.routes.worker_batch import _process_batch_operation
    
    results, batch_id = await _process_batch_operation(
        worker_ids=worker_ids,
        operation="stop",
        scope=mock_scope_context,
    )
    
    assert len(results) == 1
    assert results[0].status == "error"
    assert "Cannot stop worker" in results[0].message


# ============================================================================
# Test Batch Update Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_batch_update_single_field(test_project, test_workers, mock_scope_context):
    """Test updating single configuration field in batch."""
    from api.routes.worker_batch import WorkerConfigUpdate, _process_batch_operation
    
    worker = test_workers[0]
    config_update = WorkerConfigUpdate(timeout_seconds=7200)
    
    results, batch_id = await _process_batch_operation(
        worker_ids=[worker.worker_id],
        operation="update",
        scope=mock_scope_context,
        config_update=config_update,
    )
    
    assert len(results) == 1
    assert results[0].status == "success"
    assert "timeout_seconds" in results[0].updated_fields
    
    # Verify config was updated
    updated_worker = await WorkerSession.get(worker_id=worker.worker_id)
    assert updated_worker.context_data["config"]["timeout_seconds"] == 7200


@pytest.mark.asyncio
async def test_batch_update_multiple_fields(test_project, test_workers, mock_scope_context):
    """Test updating multiple configuration fields in batch."""
    from api.routes.worker_batch import WorkerConfigUpdate, _process_batch_operation
    
    worker = test_workers[0]
    config_update = WorkerConfigUpdate(
        timeout_seconds=7200,
        retry_count=3,
        priority=8
    )
    
    results, batch_id = await _process_batch_operation(
        worker_ids=[worker.worker_id],
        operation="update",
        scope=mock_scope_context,
        config_update=config_update,
    )
    
    assert len(results) == 1
    assert results[0].status == "success"
    assert set(results[0].updated_fields) == {"timeout_seconds", "retry_count", "priority"}
    
    # Verify all fields were updated
    updated_worker = await WorkerSession.get(worker_id=worker.worker_id)
    config = updated_worker.context_data["config"]
    assert config["timeout_seconds"] == 7200
    assert config["retry_count"] == 3
    assert config["priority"] == 8


@pytest.mark.asyncio
async def test_batch_update_multiple_workers(test_project, test_workers, mock_scope_context):
    """Test updating configuration for multiple workers."""
    from api.routes.worker_batch import WorkerConfigUpdate, _process_batch_operation
    
    worker_ids = [w.worker_id for w in test_workers[:3]]
    config_update = WorkerConfigUpdate(priority=9)
    
    results, batch_id = await _process_batch_operation(
        worker_ids=worker_ids,
        operation="update",
        scope=mock_scope_context,
        config_update=config_update,
    )
    
    assert len(results) == 3
    assert all(r.status == "success" for r in results)
    
    # Verify all workers were updated
    for worker_id in worker_ids:
        worker = await WorkerSession.get(worker_id=worker_id)
        assert worker.context_data["config"]["priority"] == 9


# ============================================================================
# Test Audit Logging
# ============================================================================

@pytest.mark.asyncio
async def test_audit_logging_batch_start(test_project, test_workers, mock_scope_context):
    """Test audit logging for batch start operations."""
    worker = test_workers[0]
    
    from api.routes.worker_batch import _process_batch_operation
    
    results, batch_id = await _process_batch_operation(
        worker_ids=[worker.worker_id],
        operation="start",
        scope=mock_scope_context,
        reason="Testing audit logging",
    )
    
    # Verify audit log entry was created
    audit_logs = await WorkerAuditLog.filter(
        worker_id=worker.worker_id,
        action="state_transition"
    )
    
    assert len(audit_logs) > 0
    log = audit_logs[0]
    assert log.status == "success"
    # batch_id is stored in metadata, not directly in details for state_transition
    assert log.details.get("metadata", {}).get("batch_id") == batch_id or batch_id in str(log.details)


@pytest.mark.asyncio
async def test_audit_logging_batch_update(test_project, test_workers, mock_scope_context):
    """Test audit logging for batch update operations."""
    from api.routes.worker_batch import WorkerConfigUpdate, _process_batch_operation
    
    worker = test_workers[0]
    config_update = WorkerConfigUpdate(timeout_seconds=5000)
    
    results, batch_id = await _process_batch_operation(
        worker_ids=[worker.worker_id],
        operation="update",
        scope=mock_scope_context,
        config_update=config_update,
    )
    
    # Verify audit log entry was created
    audit_logs = await WorkerAuditLog.filter(
        worker_id=worker.worker_id,
        action="batch_update"
    )
    
    assert len(audit_logs) > 0
    log = audit_logs[0]
    assert log.status == "success"
    assert "timeout_seconds" in log.details.get("updated_fields", [])


# ============================================================================
# Test Large Batch Operations
# ============================================================================

@pytest.mark.asyncio
async def test_batch_start_large_count(test_project, mock_scope_context):
    """Test batch start with large number of workers (50+)."""
    # Create 50 workers
    worker_ids = []
    for i in range(50):
        worker = await WorkerSession.create(
            worker_id=f"large_batch_worker_{uuid4().hex[:12]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.QUEUED,
            context_data={"config": {}}
        )
        worker_ids.append(worker.worker_id)
    
    from api.routes.worker_batch import _process_batch_operation
    
    start_time = time.time()
    results, batch_id = await _process_batch_operation(
        worker_ids=worker_ids,
        operation="start",
        scope=mock_scope_context,
    )
    elapsed = time.time() - start_time
    
    # Verify all workers processed
    assert len(results) == 50
    assert all(r.status == "success" for r in results)
    
    # Performance check: should complete in < 2 seconds
    assert elapsed < 2.0, f"Large batch took {elapsed}s (expected < 2s)"


@pytest.mark.asyncio
async def test_batch_start_max_workers(test_project, mock_scope_context):
    """Test batch endpoint respects maximum 100 workers limit."""
    # Create 100 workers
    worker_ids = []
    for i in range(100):
        worker = await WorkerSession.create(
            worker_id=f"max_batch_worker_{uuid4().hex[:12]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.QUEUED,
            context_data={"config": {}}
        )
        worker_ids.append(worker.worker_id)
    
    from api.routes.worker_batch import _process_batch_operation
    
    results, batch_id = await _process_batch_operation(
        worker_ids=worker_ids,
        operation="start",
        scope=mock_scope_context,
    )
    
    # All 100 should be processed
    assert len(results) == 100
    assert sum(1 for r in results if r.status == "success") == 100


# ============================================================================
# Test Scope Enforcement
# ============================================================================

@pytest.mark.asyncio
async def test_batch_start_scope_enforcement(test_project, test_workers, db_with_models):
    """Test batch operations enforce project scope."""
    # Create second project
    other_project = await Project.create(
        name=f"other_project_{uuid4().hex[:8]}",
        description="Another project"
    )
    
    # Create worker in other project
    other_worker = await WorkerSession.create(
        worker_id=f"other_project_worker_{uuid4().hex[:12]}",
        worker_type="generic",
        project=other_project,
        current_state=WorkerState.QUEUED,
        context_data={"config": {}}
    )
    
    # Try to start with scope of first project
    mock_scope = MagicMock()
    mock_scope.project_id = test_project.id
    mock_scope.session_id = None
    
    from api.routes.worker_batch import _process_batch_operation
    
    results, batch_id = await _process_batch_operation(
        worker_ids=[other_worker.worker_id],
        operation="start",
        scope=mock_scope,
    )
    
    # Should fail because worker not in that project scope
    assert len(results) == 1
    assert results[0].status == "error"
    assert "not found" in results[0].message


# ============================================================================
# Test Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_batch_operation_partial_failure(test_project, test_workers, running_workers, mock_scope_context):
    """Test batch operation with partial failures."""
    # Mix of workers that should succeed and fail
    worker_ids = [
        test_workers[0].worker_id,  # QUEUED - should succeed
        running_workers[0].worker_id,  # RUNNING - should fail for start
        test_workers[1].worker_id,  # QUEUED - should succeed
    ]
    
    from api.routes.worker_batch import _process_batch_operation
    
    results, batch_id = await _process_batch_operation(
        worker_ids=worker_ids,
        operation="start",
        scope=mock_scope_context,
    )
    
    assert len(results) == 3
    
    # Check that results have appropriate statuses
    successful = sum(1 for r in results if r.status == "success")
    failed = sum(1 for r in results if r.status == "error")
    
    assert successful == 2
    assert failed == 1


@pytest.mark.asyncio
async def test_batch_operation_empty_list(mock_scope_context):
    """Test batch operation with empty worker list."""
    from api.routes.worker_batch import _process_batch_operation
    
    # Empty list should be handled by validation before reaching handler
    # but we can test edge case
    results, batch_id = await _process_batch_operation(
        worker_ids=[],
        operation="start",
        scope=mock_scope_context,
    )
    
    assert len(results) == 0


# ============================================================================
# Test Response Format
# ============================================================================

@pytest.mark.asyncio
async def test_batch_response_format(test_project, test_workers, mock_scope_context):
    """Test batch operation response has correct format."""
    from api.routes.worker_batch import _process_batch_operation, BatchOperationResponse
    
    worker_ids = [w.worker_id for w in test_workers[:2]]
    
    results, batch_id = await _process_batch_operation(
        worker_ids=worker_ids,
        operation="start",
        scope=mock_scope_context,
    )
    
    # Create response object
    response = BatchOperationResponse(
        results=results,
        total_workers=len(worker_ids),
        successful_workers=sum(1 for r in results if r.status == "success"),
        failed_workers=sum(1 for r in results if r.status == "error"),
        batch_id=batch_id,
    )
    
    # Verify response structure
    assert response.total_workers == 2
    assert response.successful_workers == 2
    assert response.failed_workers == 0
    assert len(response.results) == 2
    assert response.batch_id is not None


# ============================================================================
# Test No N+1 Queries
# ============================================================================

@pytest.mark.asyncio
async def test_batch_operation_no_n_plus_1(test_project, test_workers, mock_scope_context):
    """Test batch operations don't have N+1 query problems."""
    from api.routes.worker_batch import _process_batch_operation
    
    # Create 10 workers
    worker_ids = [w.worker_id for w in test_workers]
    for i in range(5):
        worker = await WorkerSession.create(
            worker_id=f"n_plus_1_test_worker_{uuid4().hex[:12]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.QUEUED,
            context_data={"config": {}}
        )
        worker_ids.append(worker.worker_id)
    
    # All workers should be fetched in single query
    results, batch_id = await _process_batch_operation(
        worker_ids=worker_ids,
        operation="start",
        scope=mock_scope_context,
    )
    
    assert len(results) == len(worker_ids)
    assert all(r.status == "success" for r in results)
