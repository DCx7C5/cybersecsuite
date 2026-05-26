"""Task CRUD endpoints using canonical ORM models from css.core.db.models.tasks."""

from datetime import UTC, datetime
from typing import Any

from .enums import TaskStatus, TaskPriority
from .types import Task, TaskScope


async def create_task(
    team_id: int,
    orchestrator_id: str,
    query: Any,
    priority: str = "normal",
    max_retries: int = 3,
    timeout_seconds: int = 300,
) -> Task:
    """Create new task and persist to ORM (B9).
    
    Args:
        team_id: Team owner
        orchestrator_id: Target orchestrator
        query: Query object (core.types.Query)
        priority: Task priority (low/normal/high/critical)
        max_retries: Max retry attempts
        timeout_seconds: Execution timeout
    
    Returns:
        Task instance (persisted to DB)
    """
    import uuid
    from css.core.db.models.tasks import TaskAssignment

    try:
        orchestrator_pk = int(orchestrator_id)
    except ValueError as exc:
        raise ValueError(f"orchestrator_id must be numeric, got {orchestrator_id!r}") from exc
    
    task_id = str(uuid.uuid4())
    scope = TaskScope(
        id=task_id,
        team_id=team_id,
        orchestrator_id=orchestrator_id,
        query=query,
        priority=TaskPriority(priority),
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
    )
    task = Task(id=task_id, scope=scope)
    
    # Persist to ORM (B9)
    await TaskAssignment.create(
        team_id=team_id,
        orchestrator_id=orchestrator_pk,
        task_id=task_id,
        status=TaskStatus.PENDING.value,
        priority=priority,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_count=0,
        task_payload=scope.to_dict(),  # Store full scope for deserialization
    )
    
    return task


async def get_task(task_id: str) -> Task | None:
    """Retrieve task by ID from ORM (B11).
    
    Deserialize from TaskAssignment.task_payload.
    """
    from css.core.db.models.tasks import TaskAssignment
    
    try:
        task_assignment = await TaskAssignment.get(task_id=task_id)
        
        if not task_assignment.task_payload:
            return None
        
        # Deserialize TaskScope from payload
        payload = task_assignment.task_payload
        scope = _deserialize_task_scope(payload)
        
        # Reconstruct Task with current ORM state
        task = Task(
            id=task_id,
            scope=scope,
            status=_parse_task_status(task_assignment.status),
            assigned_member_id=task_assignment.assigned_member_id,
            assigned_at=task_assignment.assigned_at,
            started_at=task_assignment.started_at,
            completed_at=task_assignment.completed_at,
            retry_count=task_assignment.retry_count,
        )
        
        return task
    except Exception:
        return None


async def list_tasks(
    team_id: int,
    status: str | None = None,
    limit: int = 100,
) -> list[Task]:
    """List tasks for team.
    
    Args:
        team_id: Team filter
        status: Optional status filter
        limit: Max results
    
    Returns:
        List of tasks
    """
    from css.core.db.models.tasks import TaskAssignment
    
    query = TaskAssignment.filter(team_id=team_id)
    if status:
        query = query.filter(status=status)
    
    assignments = await query.limit(limit).all()
    
    tasks = []
    for assignment in assignments:
        if assignment.task_payload:
            scope = _deserialize_task_scope(assignment.task_payload)
            task = Task(
                id=assignment.task_id,
                scope=scope,
                status=_parse_task_status(assignment.status),
                retry_count=assignment.retry_count,
            )
            tasks.append(task)
    
    return tasks


async def update_task_status(
    task_id: str,
    new_status: str,
) -> Task:
    """Update task status.
    
    Args:
        task_id: Task to update
        new_status: New status (pending/queued/executing/completed/failed/cancelled/paused)
    
    Returns:
        Updated task
    """
    from css.core.db.models.tasks import TaskAssignment

    task_status = TaskStatus(new_status)
    task_assignment = await TaskAssignment.get_or_none(task_id=task_id)
    if task_assignment is None:
        raise ValueError(f"Task {task_id!r} not found")

    updates: dict[str, object] = {"status": task_status.value}
    if task_status == TaskStatus.EXECUTING:
        updates["started_at"] = datetime.now(UTC)
    if task_status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
        updates["completed_at"] = datetime.now(UTC)
    if task_status in (TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.PAUSED):
        updates["completed_at"] = None

    await task_assignment.save_changes(**updates)
    updated = await get_task(task_id)
    if updated is None:
        raise RuntimeError(f"Failed to hydrate task {task_id!r} after status update")
    return updated


async def cancel_task(task_id: str) -> Task:
    """Cancel task.
    
    Args:
        task_id: Task to cancel
    
    Returns:
        Cancelled task
    """
    task = await get_task(task_id)
    if task is None:
        raise ValueError(f"Task {task_id!r} not found")
    if not task.can_cancel():
        raise ValueError(f"Task {task_id!r} in state {task.status.value!r} cannot be cancelled")
    return await update_task_status(task_id, TaskStatus.CANCELLED.value)


async def retry_task(task_id: str) -> Task:
    """Retry failed task.
    
    Args:
        task_id: Task to retry
    
    Returns:
        Task in pending state
    """
    from css.core.db.models.tasks import TaskAssignment

    task = await get_task(task_id)
    if task is None:
        raise ValueError(f"Task {task_id!r} not found")
    if not task.can_retry():
        raise ValueError(
            f"Task {task_id!r} in state {task.status.value!r} cannot be retried "
            f"(retry_count={task.retry_count}, max_retries={task.scope.max_retries})"
        )

    task_assignment = await TaskAssignment.get_or_none(task_id=task_id)
    if task_assignment is None:
        raise ValueError(f"Task {task_id!r} not found")

    await task_assignment.save_changes(
        status=TaskStatus.PENDING.value,
        completed_at=None,
        started_at=None,
        assigned_member_id=None,
    )
    retried = await get_task(task_id)
    if retried is None:
        raise RuntimeError(f"Failed to hydrate task {task_id!r} after retry")
    return retried


# ── Helper functions for serialization/deserialization ──────────────────────

def _deserialize_task_scope(payload: dict[str, Any]) -> TaskScope:
    """Deserialize TaskScope from ORM JSON payload."""
    from css.core.types import Query
    from datetime import datetime
    
    # Reconstruct Query from payload
    query_data = payload.get("query", {})
    query = Query(
        id=query_data.get("id", "unknown"),
        prompt=query_data.get("prompt", ""),
        mode=query_data.get("mode", "blue"),
        agent_name=query_data.get("agent_name", "cybersec-agents"),
        metadata=query_data.get("metadata", {}),
        created_at=datetime.fromisoformat(query_data.get("created_at", datetime.now().isoformat())),
    )
    
    # Reconstruct TaskScope
    scope = TaskScope(
        id=payload.get("id", "unknown"),
        team_id=payload.get("team_id", 0),
        orchestrator_id=payload.get("orchestrator_id", ""),
        query=query,
        priority=TaskPriority(payload.get("priority", "normal")),
        max_retries=payload.get("max_retries", 3),
        timeout_seconds=payload.get("timeout_seconds", 300),
        metadata=payload.get("metadata", {}),
    )
    
    return scope


def _parse_task_status(status_str: str) -> TaskStatus:
    """Parse TaskStatus from string."""
    try:
        return TaskStatus(status_str)
    except ValueError:
        return TaskStatus.PENDING


__all__ = [
    "create_task",
    "get_task",
    "list_tasks",
    "update_task_status",
    "cancel_task",
    "retry_task",
]
