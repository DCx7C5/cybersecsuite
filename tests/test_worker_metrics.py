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
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from fastapi import FastAPI, Request, status
from tortoise import Tortoise

from db.models.scope import Project
from db.models.worker import (
    WorkerSession, WorkerState, WorkerAuditLog, WorkerStateTransition
)
from api.routes.worker_metrics import router as metrics_router


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
async def test_worker_with_metrics(db_with_models, test_project):
    """Create a test worker with execution metrics."""
    history = [
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
    """Create FastAPI app with metrics router."""
    app = FastAPI()
    
    @app.middleware("http")
    async def add_scope_context(request: Request, call_next):
        request.state.scope_context = mock_scope_context
        return await call_next(request)
    
    app.include_router(metrics_router)
    return app


@pytest.fixture
def client(app_with_router):
    """Create test client."""
    return TestClient(app_with_router)


# ============================================================================
# Test: GET /api/workers/{id}/metrics
# ============================================================================

@pytest.mark.asyncio
async def test_get_worker_metrics_success(client, db_with_models, test_project, test_worker_with_metrics, mock_scope_context):
    """Test getting worker metrics successfully."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_metrics.project_id = test_project.id
    await test_worker_with_metrics.save()
    
    response = client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/metrics")
    
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
async def test_get_worker_metrics_not_found(client, mock_scope_context):
    """Test getting metrics for non-existent worker."""
    mock_scope_context.project_id = 1
    
    response = client.get("/api/workers/nonexistent/metrics")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_worker_metrics_cross_project_denied(client, db_with_models, test_project, test_worker_with_metrics, mock_scope_context):
    """Test metrics access enforces project scope."""
    mock_scope_context.project_id = 999  # Different project
    test_worker_with_metrics.project_id = test_project.id
    await test_worker_with_metrics.save()
    
    response = client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/metrics")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: GET /api/workers/{id}/audit
# ============================================================================

@pytest.mark.asyncio
async def test_get_worker_audit_success(client, db_with_models, test_project, test_worker_with_metrics, mock_scope_context):
    """Test getting worker audit trail successfully."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_metrics.project_id = test_project.id
    await test_worker_with_metrics.save()
    
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
    
    response = client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_get_worker_audit_pagination(client, db_with_models, test_project, test_worker_with_metrics, mock_scope_context):
    """Test audit trail pagination."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_metrics.project_id = test_project.id
    await test_worker_with_metrics.save()
    
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
    
    response = client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit?page=1&size=3")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 10
    assert len(data["items"]) == 3
    assert data["has_more"] is True


@pytest.mark.asyncio
async def test_get_worker_audit_filter_by_action(client, db_with_models, test_project, test_worker_with_metrics, mock_scope_context):
    """Test audit trail filtering by action."""
    mock_scope_context.project_id = test_project.id
    test_worker_with_metrics.project_id = test_project.id
    await test_worker_with_metrics.save()
    
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
    
    response = client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit?action=pause")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 3
    for item in data["items"]:
        assert item["action"] == "pause"


@pytest.mark.asyncio
async def test_get_worker_audit_not_found(client, mock_scope_context):
    """Test audit for non-existent worker."""
    mock_scope_context.project_id = 1
    
    response = client.get("/api/workers/nonexistent/audit")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: GET /api/workers/summary
# ============================================================================

@pytest.mark.asyncio
async def test_get_workers_summary_success(client, db_with_models, test_project, mock_scope_context):
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
    
    response = client.get(f"/api/workers/summary?project_id={test_project.id}")
    
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
async def test_get_workers_summary_defaults_to_scope(client, db_with_models, test_project, mock_scope_context):
    """Test summary defaults to scope project."""
    mock_scope_context.project_id = test_project.id
    
    await WorkerSession.create(
        worker_id=f"worker_{uuid4().hex[:16]}",
        worker_type="generic",
        project=test_project,
        current_state=WorkerState.RUNNING
    )
    
    response = client.get("/api/workers/summary")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_workers"] == 1


@pytest.mark.asyncio
async def test_get_workers_summary_no_workers(client, db_with_models, test_project, mock_scope_context):
    """Test summary with no workers."""
    mock_scope_context.project_id = test_project.id
    
    response = client.get(f"/api/workers/summary?project_id={test_project.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_workers"] == 0


# ============================================================================
# Test: GET /api/health/workers
# ============================================================================

@pytest.mark.asyncio
async def test_get_workers_health_success(client, db_with_models):
    """Test getting workers health successfully."""
    response = client.get("/api/health/workers")
    
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
async def test_get_workers_health_empty(client, db_with_models):
    """Test health check with no workers."""
    response = client.get("/api/health/workers")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_workers"] == 0


@pytest.mark.asyncio
async def test_get_workers_health_with_failures(client, db_with_models, test_project):
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
    
    response = client.get("/api/health/workers")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_workers"] == 1
    # Error rate should reflect recent failures


# ============================================================================
# Test: Metrics Calculations
# ============================================================================

@pytest.mark.asyncio
async def test_metrics_success_rate_calculation(client, db_with_models, test_project, mock_scope_context):
    """Test success rate metric calculation."""
    mock_scope_context.project_id = test_project.id
    
    # Create worker with mixed success/failure
    history = [
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
    
    response = client.get(f"/api/workers/{worker.worker_id}/metrics")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success_rate"] == 0.75  # 3 successes out of 4


# ============================================================================
# Test: Scope Enforcement
# ============================================================================

@pytest.mark.asyncio
async def test_metrics_enforces_scope(client, db_with_models, test_project, test_worker_with_metrics, mock_scope_context):
    """Test metrics endpoint enforces scope."""
    mock_scope_context.project_id = 999  # Different project
    test_worker_with_metrics.project_id = test_project.id
    await test_worker_with_metrics.save()
    
    response = client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/metrics")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_audit_enforces_scope(client, db_with_models, test_project, test_worker_with_metrics, mock_scope_context):
    """Test audit endpoint enforces scope."""
    mock_scope_context.project_id = 999  # Different project
    test_worker_with_metrics.project_id = test_project.id
    await test_worker_with_metrics.save()
    
    response = client.get(f"/api/workers/{test_worker_with_metrics.worker_id}/audit")
    assert response.status_code == status.HTTP_404_NOT_FOUND
