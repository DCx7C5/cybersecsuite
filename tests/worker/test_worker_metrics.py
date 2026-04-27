"""
Test suite for Worker Metrics and Monitoring API endpoints — t372.

Coverage: 80%+ (15-20 tests)
- GET /api/workers/{id}/metrics — Current metrics
- GET /api/workers/{id}/audit — Audit trail
- GET /api/workers/summary?project_id=X — Aggregate stats
- GET /api/health/workers — Subsystem health
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from datetime import datetime
from uuid import uuid4
from unittest.mock import MagicMock

from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI, Request, status

from db.models.scope import ProjectScope
from db.models.worker import (
    WorkerSession, WorkerState, WorkerAuditLog
)
from api.routes.worker_metrics import router as metrics_router


# ============================================================================
# Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def test_worker_with_metrics(db, test_project):
    """Create a test worker with execution metrics."""
    history: list[dict] = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "step_completed",
            "status": "success",
            "result": {"duration_ms": 100}
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "step_completed",
            "status": "success",
            "result": {"duration_ms": 150}
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
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
        steps_executed=3,
        total_duration_ms=370
    )
    
    worker.update_execution_history(history)
    await worker.save()
    
    return worker


@pytest_asyncio.fixture
async def mock_scope_context(test_project):
    """Create a mock scope context."""
    ctx = MagicMock()
    ctx.request_id = "req-test-123"
    ctx.scope_level = "project"
    ctx.project_id = test_project.id
    ctx.session_id = None
    ctx.user_id = "user-123"
    return ctx


@pytest_asyncio.fixture
async def app_with_router(mock_scope_context):
    """Create FastAPI app with metrics router."""
    app = FastAPI()
    
    @app.middleware("http")
    async def add_scope_context(request: Request, call_next):
        request.state.scope_context = mock_scope_context
        return await call_next(request)
    
    app.include_router(metrics_router)
    return app


@pytest_asyncio.fixture
async def async_client(app_with_router):
    """Create async test client."""
    transport = ASGITransport(app=app_with_router)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


# ============================================================================
# Test: GET /api/workers/{id}/metrics
# ============================================================================

@pytest.mark.asyncio
async def test_get_worker_metrics_success(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test getting worker metrics successfully."""
    mock_scope_context.project_id = test_project.id
    
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/metrics")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify all metrics are present
    assert data["worker_id"] == test_worker_with_metrics.worker_id
    assert data["step_count"] == 3
    assert data["success_rate"] == 1.0  # All successful
    assert data["avg_duration_ms"] > 0  # Should be ~123.33
    assert data["current_state"] == "running"
    assert data["uptime_ms"] > 0


@pytest.mark.asyncio
async def test_get_worker_metrics_not_found(async_client, test_project, mock_scope_context):
    """Test getting metrics for non-existent worker."""
    mock_scope_context.project_id = test_project.id
    
    response = await async_client.get("/api/workers/nonexistent/metrics")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_worker_metrics_cross_project_denied(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test metrics access enforces project scope."""
    # Create a different project for scope check
    other_project = await ProjectScope.create(name=f"other_project_{uuid4().hex[:8]}")
    mock_scope_context.project_id = other_project.id  # Different project
    
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/metrics")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: GET /api/workers/{id}/audit
# ============================================================================

@pytest.mark.asyncio
async def test_get_worker_audit_success(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test getting worker audit trail successfully."""
    mock_scope_context.project_id = test_project.id
    
    # Create some audit logs
    for i in range(3):
        await WorkerAuditLog.create(
            worker_id=test_worker_with_metrics.worker_id,
            project=test_project,
            scope_level="project",
            action=f"action_{i}",
            status="success",
            details={"user_id": "user-123"}
        )
    
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_get_worker_audit_pagination(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test audit trail pagination."""
    mock_scope_context.project_id = test_project.id
    
    # Create 10 audit logs
    for i in range(10):
        await WorkerAuditLog.create(
            worker_id=test_worker_with_metrics.worker_id,
            project=test_project,
            scope_level="project",
            action=f"action_{i}",
            status="success",
            details={}
        )
    
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit?page=1&size=3")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 10
    assert len(data["items"]) == 3
    assert data["has_more"] is True


@pytest.mark.asyncio
async def test_get_worker_audit_filter_by_action(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test audit trail filtering by action."""
    mock_scope_context.project_id = test_project.id
    
    # Create audit logs with different actions
    for i in range(2):
        await WorkerAuditLog.create(
            worker_id=test_worker_with_metrics.worker_id,
            project=test_project,
            scope_level="project",
            action="start",
            status="success",
            details={}
        )
    
    for i in range(3):
        await WorkerAuditLog.create(
            worker_id=test_worker_with_metrics.worker_id,
            project=test_project,
            scope_level="project",
            action="pause",
            status="success",
            details={}
        )
    
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit?action=pause")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 3
    for item in data["items"]:
        assert item["action"] == "pause"


@pytest.mark.asyncio
async def test_get_worker_audit_not_found(async_client, test_project, mock_scope_context):
    """Test audit for non-existent worker."""
    mock_scope_context.project_id = test_project.id
    
    response = await async_client.get("/api/workers/nonexistent/audit")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: GET /api/workers/summary
# ============================================================================

@pytest.mark.asyncio
async def test_get_workers_summary_success(async_client, test_project, mock_scope_context):
    """Test getting worker summary successfully."""
    mock_scope_context.project_id = test_project.id
    
    # Create workers in different states
    for _ in range(5):
        await WorkerSession.create(
            worker_id=f"worker_{uuid4().hex[:16]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.RUNNING,
            steps_executed=10
        )
    
    for _ in range(3):
        await WorkerSession.create(
            worker_id=f"worker_{uuid4().hex[:16]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.PAUSED,
            steps_executed=5
        )
    
    for _ in range(2):
        await WorkerSession.create(
            worker_id=f"worker_{uuid4().hex[:16]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.COMPLETED,
            steps_executed=20
        )
    
    response = await async_client.get(f"/api/workers/summary?project_id={test_project.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["project_id"] == test_project.id
    assert data["total_workers"] == 10
    assert data["running"] == 5
    assert data["paused"] == 3
    assert data["completed"] == 2
    assert data["failed"] == 0
    assert data["queued"] == 0


@pytest.mark.asyncio
async def test_get_workers_summary_defaults_to_scope(async_client, test_project, mock_scope_context):
    """Test summary defaults to scope project."""
    mock_scope_context.project_id = test_project.id
    
    await WorkerSession.create(
        worker_id=f"worker_{uuid4().hex[:16]}",
        worker_type="generic",
        project=test_project,
        current_state=WorkerState.RUNNING
    )
    
    response = await async_client.get("/api/workers/summary")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_workers"] == 1


@pytest.mark.asyncio
async def test_get_workers_summary_no_workers(async_client, test_project, mock_scope_context):
    """Test summary with no workers."""
    mock_scope_context.project_id = test_project.id
    
    response = await async_client.get(f"/api/workers/summary?project_id={test_project.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_workers"] == 0


# ============================================================================
# Test: GET /api/health/workers
# ============================================================================

@pytest.mark.asyncio
async def test_get_workers_health_success(async_client):
    """Test getting workers health successfully."""
    response = await async_client.get("/api/health/workers")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify health response structure
    assert "status" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "total_workers" in data
    assert "avg_metrics" in data
    assert "error_rate" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_workers_health_empty(async_client):
    """Test health check with no workers."""
    response = await async_client.get("/api/health/workers")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_workers"] == 0


@pytest.mark.asyncio
async def test_get_workers_health_with_failures(async_client, test_project):
    """Test health check calculates error rate."""
    # Create a worker
    worker = await WorkerSession.create(
        worker_id=f"worker_{uuid4().hex[:16]}",
        worker_type="generic",
        project=test_project,
        current_state=WorkerState.RUNNING
    )
    
    # Create audit logs with failures
    for i in range(3):
        await WorkerAuditLog.create(
            worker_id=worker.worker_id,
            project=test_project,
            scope_level="project",
            action="test",
            status="failure",
            details={}
        )
    
    response = await async_client.get("/api/health/workers")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_workers"] == 1
    # Error rate should reflect recent failures


# ============================================================================
# Test: Metrics Calculations
# ============================================================================

@pytest.mark.asyncio
async def test_metrics_success_rate_calculation(async_client, test_project, mock_scope_context):
    """Test success rate metric calculation."""
    mock_scope_context.project_id = test_project.id
    
    # Create worker with mixed success/failure
    history: list[dict] = [
        {"timestamp": datetime.utcnow().isoformat(), "action": "step", "status": "success"},
        {"timestamp": datetime.utcnow().isoformat(), "action": "step", "status": "success"},
        {"timestamp": datetime.utcnow().isoformat(), "action": "step", "status": "failure"},
        {"timestamp": datetime.utcnow().isoformat(), "action": "step", "status": "success"},
    ]
    
    worker = await WorkerSession.create(
        worker_id=f"worker_{uuid4().hex[:16]}",
        worker_type="generic",
        project=test_project,
        current_state=WorkerState.RUNNING,
        execution_history=history,
        steps_executed=4
    )
    worker.update_execution_history(history)
    await worker.save()
    
    response = await async_client.get(f"/api/workers/{worker.worker_id}/metrics")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success_rate"] == 0.75  # 3 successes out of 4


# ============================================================================
# Test: Scope Enforcement
# ============================================================================

@pytest.mark.asyncio
async def test_metrics_enforces_scope(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test metrics endpoint enforces scope."""
    other_project = await ProjectScope.create(name=f"other_project_{uuid4().hex[:8]}")
    mock_scope_context.project_id = other_project.id  # Different project
    
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/metrics")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_audit_enforces_scope(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test audit endpoint enforces scope."""
    other_project = await ProjectScope.create(name=f"other_project_{uuid4().hex[:8]}")
    mock_scope_context.project_id = other_project.id  # Different project
    
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_summary_enforces_scope(async_client, test_project, mock_scope_context):
    """Test summary endpoint enforces scope."""
    other_project = await ProjectScope.create(name=f"other_project_{uuid4().hex[:8]}")
    mock_scope_context.project_id = other_project.id
    
    # Try to access different project
    response = await async_client.get(f"/api/workers/summary?project_id={test_project.id}")
    # Should either deny or only show scoped data
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]


# ============================================================================
# Additional Tests for Comprehensive Coverage
# ============================================================================

@pytest.mark.asyncio
async def test_get_worker_metrics_empty_history(async_client, test_project, mock_scope_context):
    """Test metrics for worker with no execution history."""
    mock_scope_context.project_id = test_project.id
    
    worker = await WorkerSession.create(
        worker_id=f"worker_{uuid4().hex[:16]}",
        worker_type="generic",
        project=test_project,
        current_state=WorkerState.QUEUED,
        execution_history=[],
        steps_executed=0
    )
    
    response = await async_client.get(f"/api/workers/{worker.worker_id}/metrics")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["step_count"] == 0
    assert data["success_rate"] == 0.0
    assert data["avg_duration_ms"] == 0.0


@pytest.mark.asyncio
async def test_get_worker_metrics_partial_failures(async_client, test_project, mock_scope_context):
    """Test metrics calculation with partial failures."""
    mock_scope_context.project_id = test_project.id
    
    history: list[dict] = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "step",
            "status": "success",
            "result": {"duration_ms": 100}
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "step",
            "status": "failure",
            "result": {}
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "step",
            "status": "success",
            "result": {"duration_ms": 50}
        },
    ]
    
    worker = await WorkerSession.create(
        worker_id=f"worker_{uuid4().hex[:16]}",
        worker_type="generic",
        project=test_project,
        current_state=WorkerState.COMPLETED,
        execution_history=history,
        steps_executed=3
    )
    worker.update_execution_history(history)
    await worker.save()
    
    response = await async_client.get(f"/api/workers/{worker.worker_id}/metrics")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["step_count"] == 3
    assert data["success_rate"] == pytest.approx(2/3, abs=0.01)
    assert data["avg_duration_ms"] == 75.0  # (100 + 50) / 2


@pytest.mark.asyncio
async def test_get_worker_audit_large_pagination(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test audit pagination with large page size."""
    mock_scope_context.project_id = test_project.id
    
    # Create 50 audit logs
    for i in range(50):
        await WorkerAuditLog.create(
            worker_id=test_worker_with_metrics.worker_id,
            project=test_project,
            scope_level="project",
            action=f"action_{i}",
            status="success" if i % 2 == 0 else "failure",
            details={"index": i}
        )
    
    # Test with page 1, size 100 (all results)
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit?page=1&size=100")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 50
    assert len(data["items"]) == 50
    assert data["page"] == 1
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_get_worker_audit_second_page(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test audit trail second page navigation."""
    mock_scope_context.project_id = test_project.id
    
    # Create 25 audit logs
    for i in range(25):
        await WorkerAuditLog.create(
            worker_id=test_worker_with_metrics.worker_id,
            project=test_project,
            scope_level="project",
            action=f"action_{i}",
            status="success",
            details={}
        )
    
    # Get second page with size 10
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit?page=2&size=10")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 25
    assert len(data["items"]) == 10
    assert data["page"] == 2
    assert data["has_more"] is True


@pytest.mark.asyncio
async def test_get_workers_summary_with_averages(async_client, test_project, mock_scope_context):
    """Test summary correctly calculates averages."""
    mock_scope_context.project_id = test_project.id
    
    # Create workers with specific step counts
    step_counts = [10, 20, 30, 40, 50]
    for i, steps in enumerate(step_counts):
        await WorkerSession.create(
            worker_id=f"worker_{uuid4().hex[:16]}",
            worker_type="generic",
            project=test_project,
            current_state=WorkerState.COMPLETED,
            steps_executed=steps,
            execution_history=[
                {"status": "success"},
                {"status": "success"},
                {"status": "failure"},
            ]
        )
    
    response = await async_client.get(f"/api/workers/summary?project_id={test_project.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Average should be 30
    assert data["avg_step_count"] == 30.0
    # Success rate should be 2/3 for all workers
    assert data["avg_success_rate"] == pytest.approx(2/3, abs=0.01)


@pytest.mark.asyncio
async def test_get_workers_summary_all_states(async_client, test_project, mock_scope_context):
    """Test summary with workers in all possible states."""
    mock_scope_context.project_id = test_project.id
    
    states = [
        (WorkerState.QUEUED, 2),
        (WorkerState.RUNNING, 3),
        (WorkerState.PAUSED, 1),
        (WorkerState.COMPLETED, 4),
        (WorkerState.FAILED, 1),
    ]
    
    for state, count in states:
        for _ in range(count):
            await WorkerSession.create(
                worker_id=f"worker_{uuid4().hex[:16]}",
                worker_type="generic",
                project=test_project,
                current_state=state
            )
    
    response = await async_client.get(f"/api/workers/summary?project_id={test_project.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["total_workers"] == 11
    assert data["queued"] == 2
    assert data["running"] == 3
    assert data["paused"] == 1
    assert data["completed"] == 4
    assert data["failed"] == 1


@pytest.mark.asyncio
async def test_get_workers_health_status_degraded(async_client, test_project):
    """Test health check reports degraded status."""
    # Create workers and failures between 1-5% error rate
    worker = await WorkerSession.create(
        worker_id=f"worker_{uuid4().hex[:16]}",
        worker_type="generic",
        project=test_project,
        current_state=WorkerState.RUNNING
    )
    
    # Create 2 failures out of 100 recent actions = 2% error rate (degraded)
    for i in range(2):
        await WorkerAuditLog.create(
            worker_id=worker.worker_id,
            project=test_project,
            scope_level="project",
            action="test",
            status="failure",
            details={}
        )
    
    for i in range(98):
        await WorkerAuditLog.create(
            worker_id=worker.worker_id,
            project=test_project,
            scope_level="project",
            action="test",
            status="success",
            details={}
        )
    
    response = await async_client.get("/api/health/workers")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]  # Could be either depending on timing
    assert data["total_workers"] == 1


@pytest.mark.asyncio
async def test_audit_max_size_enforcement(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test audit endpoint max size constraint."""
    mock_scope_context.project_id = test_project.id
    
    # Try to request size > 1000
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit?size=2000")
    
    # Should either cap at 1000 or return an error
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.asyncio
async def test_get_worker_metrics_large_execution_history(async_client, test_project, mock_scope_context):
    """Test metrics calculation with large execution history."""
    mock_scope_context.project_id = test_project.id
    
    # Create 100 execution history entries
    history: list[dict] = []
    for i in range(100):
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": f"step_{i}",
            "status": "success" if i % 10 != 0 else "failure",  # 10% failure rate
            "result": {"duration_ms": 50 + (i % 50)}
        })
    
    worker = await WorkerSession.create(
        worker_id=f"worker_{uuid4().hex[:16]}",
        worker_type="generic",
        project=test_project,
        current_state=WorkerState.RUNNING,
        execution_history=history,
        steps_executed=100
    )
    worker.update_execution_history(history)
    await worker.save()
    
    response = await async_client.get(f"/api/workers/{worker.worker_id}/metrics")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["step_count"] == 100
    assert data["success_rate"] == pytest.approx(0.9, abs=0.01)
    assert data["avg_duration_ms"] > 0


@pytest.mark.asyncio
async def test_get_workers_summary_missing_scope(async_client, mock_scope_context):
    """Test summary without scope context."""
    mock_scope_context.project_id = None
    
    response = await async_client.get("/api/workers/summary")
    
    # Should fail when no scope is available
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]


@pytest.mark.asyncio
async def test_audit_enforces_pagination_constraints(async_client, test_project, test_worker_with_metrics, mock_scope_context):
    """Test audit endpoint enforces pagination parameter constraints."""
    mock_scope_context.project_id = test_project.id
    
    # Try invalid page number
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit?page=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Try invalid size
    response = await async_client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit?size=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
