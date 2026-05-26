"""Scheduler endpoints."""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional, Dict
from datetime import datetime, timezone
import msgspec
from css.core.types.base_endpoint import EndpointModel
from .models import ScheduledTask

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


class TaskCreate(EndpointModel, kw_only=True):
    task_type: str
    name: str
    description: str = ""
    cron_expression: str
    timezone: str = "UTC"
    task_config: Dict = {}


class TaskResponse(EndpointModel, kw_only=True):
    id: int
    task_id: str
    task_type: str
    name: str
    cron_expression: str
    is_active: bool
    next_run_at: Optional[datetime]


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    req: TaskCreate,
    org_id: int = Query(...),
):
    """Create scheduled task."""
    task_id = f"TASK-{org_id}-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
    task = await ScheduledTask.create(
        organization_id=org_id,
        task_id=task_id,
        task_type=req.task_type,
        name=req.name,
        description=req.description,
        cron_expression=req.cron_expression,
        timezone=req.timezone,
        task_config=req.task_config,
    )
    return TaskResponse(**{f: getattr(task, f) for f in TaskResponse.__struct_fields__})


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    org_id: int = Query(...),
    is_active: Optional[bool] = None,
):
    """List scheduled tasks."""
    query = ScheduledTask.filter(organization_id=org_id)
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    tasks = await query.all()
    return [TaskResponse(**{f: getattr(t, f) for f in TaskResponse.__struct_fields__}) for t in tasks]


@router.post("/tasks/{task_id}/run", status_code=status.HTTP_202_ACCEPTED)
async def run_task_now(
    task_id: str,
    org_id: int = Query(...),
):
    """Trigger immediate execution of task."""
    task = await ScheduledTask.get_or_none(organization_id=org_id, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # TODO: Queue task for execution
    return {"status": "queued"}


__all__ = ["router"]
