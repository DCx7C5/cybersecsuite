"""
Background Worker Monitor — Metrics and observability for background workers.

Provides metrics endpoint returning:
- Worker count and activity status
- Queue depth and pending tasks
- Performance metrics (latency, throughput)
- VRAM usage if available
- Error counts and recent errors
"""


import logging
import time
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.transactions import in_transaction

logger = logging.getLogger("worker_monitor")


class WorkerMetrics(BaseModel):
    """Per-worker metrics."""

    worker_id: str
    worker_type: str
    is_active: bool
    health_status: str  # healthy, degraded, unhealthy
    active_task_count: int = 0
    queue_depth: int = 0
    total_tasks_processed: int = 0
    avg_task_duration_ms: int = 0
    error_count: int = 0
    consecutive_errors: int = 0
    last_heartbeat_seconds_ago: float
    recent_errors: list[dict[str, Any]] = Field(default_factory=list)


class WorkerMonitorMetrics(BaseModel):
    """Overall worker monitoring metrics."""

    timestamp: float
    worker_count: int = 0
    active_workers: int = 0
    total_queue_depth: int = 0
    total_tasks_processed: int = 0
    total_errors: int = 0
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    vram_usage_mb: Optional[float] = None
    vram_available_mb: Optional[float] = None
    vram_percent: Optional[float] = None
    workers: list[WorkerMetrics] = Field(default_factory=list)
    uptime_seconds: int = 0
    last_updated_at: str = ""


_APP_START_TIME = time.time()


async def detect_vram_usage() -> dict[str, float | None]:
    """
    Detect VRAM usage via nvidia-smi or alternative GPU monitoring.

    Returns:
        dict with keys: used_mb, available_mb, percent
    """
    try:
        # Try nvidia-smi first
        async with httpx.AsyncClient(timeout=2.0) as client:
            try:
                # Query GPU memory
                result = await client.get(
                    "http://localhost:8888/api/gpu/memory",  # Common GPU monitoring port
                    timeout=1.0,
                )
                if result.status_code == 200:
                    data = result.json()
                    return {
                        "used_mb": data.get("used"),
                        "available_mb": data.get("available"),
                        "percent": data.get("percent"),
                    }
            except Exception:
                pass

        # Fallback: try nvidia-smi command
        import subprocess
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.used,memory.free",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(",")
                used = int(parts[0].strip())
                free = int(parts[1].strip())
                total = used + free
                return {
                    "used_mb": used,
                    "available_mb": free,
                    "percent": round((used / total) * 100, 2) if total > 0 else 0,
                }
        except Exception:
            pass

    except Exception as e:
        logger.debug(f"VRAM detection failed: {e}")

    return {"used_mb": None, "available_mb": None, "percent": None}


async def get_worker_monitor_metrics() -> WorkerMonitorMetrics:
    """
    Collect metrics from all background workers.

    Returns:
        WorkerMonitorMetrics with aggregated worker data
    """
    try:
        from db.models.worker_context import WorkerContext

        now = time.time()
        uptime_seconds = int(now - _APP_START_TIME)

        # Get all active workers
        workers_data = await WorkerContext.filter(is_active=True).all()

        # Calculate metrics per worker
        worker_metrics: list[WorkerMetrics] = []
        total_queue_depth = 0
        total_tasks_processed = 0
        total_errors = 0
        total_latency_ms = 0.0

        for worker in workers_data:
            last_heartbeat_delta = now - worker.last_heartbeat_at.timestamp() if worker.last_heartbeat_at else 0

            # Determine health status based on error rate
            health_status = worker.health_status
            if worker.consecutive_errors > 5:
                health_status = "unhealthy"
            elif worker.consecutive_errors > 2:
                health_status = "degraded"

            wm = WorkerMetrics(
                worker_id=worker.worker_id,
                worker_type=worker.worker_type,
                is_active=worker.is_active,
                health_status=health_status,
                active_task_count=worker.active_task_count,
                queue_depth=worker.queue_depth,
                total_tasks_processed=worker.total_tasks_processed,
                avg_task_duration_ms=worker.avg_task_duration_ms,
                error_count=worker.error_count,
                consecutive_errors=worker.consecutive_errors,
                last_heartbeat_seconds_ago=last_heartbeat_delta,
                recent_errors=worker.recent_errors or [],
            )
            worker_metrics.append(wm)

            # Aggregate
            total_queue_depth += worker.queue_depth
            total_tasks_processed += worker.total_tasks_processed
            total_errors += worker.error_count
            total_latency_ms += worker.total_processing_time_ms

        # Get VRAM metrics
        vram_data = await detect_vram_usage()

        # Calculate averages
        avg_latency_ms = (
            total_latency_ms / len(worker_metrics) if worker_metrics else 0
        )

        return WorkerMonitorMetrics(
            timestamp=now,
            worker_count=len(worker_metrics),
            active_workers=sum(1 for w in worker_metrics if w.is_active),
            total_queue_depth=total_queue_depth,
            total_tasks_processed=total_tasks_processed,
            total_errors=total_errors,
            total_latency_ms=total_latency_ms,
            avg_latency_ms=avg_latency_ms,
            vram_usage_mb=vram_data.get("used_mb"),
            vram_available_mb=vram_data.get("available_mb"),
            vram_percent=vram_data.get("percent"),
            workers=worker_metrics,
            uptime_seconds=uptime_seconds,
            last_updated_at=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to collect worker metrics: {e}")
        return WorkerMonitorMetrics(
            timestamp=time.time(),
            uptime_seconds=int(time.time() - _APP_START_TIME),
            last_updated_at=datetime.utcnow().isoformat(),
        )


async def api_worker_metrics(request: Request) -> JSONResponse:
    """
    GET /api/v1/metrics/workers
    
    Return background worker monitoring metrics.

    Returns:
        JSON with worker metrics, VRAM, latency, error counts
    """
    metrics = await get_worker_monitor_metrics()
    return JSONResponse(content=metrics.model_dump(), status_code=200)


async def api_worker_health(request: Request) -> JSONResponse:
    """
    GET /api/v1/health/workers
    
    Quick health check for all workers.

    Returns:
        JSON with worker count, active count, total errors
    """
    try:
        metrics = await get_worker_monitor_metrics()
        return JSONResponse(
            content={
                "status": "healthy" if metrics.total_errors == 0 else "degraded",
                "worker_count": metrics.worker_count,
                "active_workers": metrics.active_workers,
                "total_queue_depth": metrics.total_queue_depth,
                "total_errors": metrics.total_errors,
                "unhealthy_workers": [
                    w.worker_id
                    for w in metrics.workers
                    if w.health_status == "unhealthy"
                ],
            },
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Worker health check failed: {e}")
        return JSONResponse(
            content={"error": str(e), "status": "error"},
            status_code=500,
        )


async def cleanup_stale_workers(stale_threshold_seconds: int = 3600) -> int:
    """
    Clean up stale worker contexts (no heartbeat for threshold time).

    Args:
        stale_threshold_seconds: Seconds of inactivity before marking stale

    Returns:
        Number of workers cleaned up
    """
    try:
        from db.models.worker_context import WorkerContext

        cutoff_time = datetime.utcnow() - timedelta(seconds=stale_threshold_seconds)

        async with in_transaction():
            stale_workers = await WorkerContext.filter(
                last_heartbeat_at__lt=cutoff_time
            ).all()

            for worker in stale_workers:
                worker.is_active = False
                await worker.save()

            deleted_count = len(stale_workers)
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} stale workers")
            return deleted_count

    except Exception as e:
        logger.error(f"Failed to cleanup stale workers: {e}")
        return 0


async def update_worker_context(
    session_id: int,
    worker_id: str,
    worker_type: str = "generic",
    active_task_count: int = 0,
    queue_depth: int = 0,
    error_count: int = 0,
    task_duration_ms: int = 0,
) -> None:
    """
    Update worker context with latest metrics.

    Args:
        session_id: Session ID
        worker_id: Unique worker ID
        worker_type: Worker type
        active_task_count: Current active task count
        queue_depth: Current queue depth
        error_count: Total error count
        task_duration_ms: Latest task duration in ms
    """
    try:
        from db.models.worker_context import WorkerContext
        from db.models.llm_session import Session

        session = await Session.get_or_none(id=session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return

        worker_context, _ = await WorkerContext.get_or_create(
            session=session,
            worker_id=worker_id,
            defaults={
                "worker_type": worker_type,
                "is_active": True,
                "health_status": "healthy",
            },
        )

        # Update metrics
        worker_context.active_task_count = active_task_count
        worker_context.queue_depth = queue_depth
        worker_context.error_count = error_count
        worker_context.is_active = True
        worker_context.health_status = (
            "healthy"
            if error_count == 0
            else ("degraded" if error_count < 5 else "unhealthy")
        )

        # Update task duration metrics
        if task_duration_ms > 0:
            old_total = worker_context.total_processing_time_ms
            old_count = worker_context.total_tasks_processed
            new_count = old_count + 1

            worker_context.total_processing_time_ms = old_total + task_duration_ms
            worker_context.total_tasks_processed = new_count
            worker_context.avg_task_duration_ms = int(
                worker_context.total_processing_time_ms / new_count
            )

            if task_duration_ms > worker_context.max_task_duration_ms:
                worker_context.max_task_duration_ms = task_duration_ms

        await worker_context.save()

    except Exception as e:
        logger.error(f"Failed to update worker context: {e}")
