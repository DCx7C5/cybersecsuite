"""Task CRUD endpoints."""

from typing import Any, Optional

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
    from css.core.db.models import TaskAssignment
    
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
        orchestrator_id=orchestrator_id,
        task_id=task_id,
        status=TaskStatus.PENDING.value,
        priority=priority,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_count=0,
        task_payload=scope.to_dict(),  # Store full scope for deserialization
    )
    
    return task


async def get_task(task_id: str) -> Optional[Task]:
    """Retrieve task by ID from ORM (B11).
    
    Deserialize from TaskAssignment.task_payload.
    """
    from css.core.db.models import TaskAssignment
    
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
    status: Optional[str] = None,
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
    from css.core.db.models import TaskAssignment
    
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
    pass


async def cancel_task(task_id: str) -> Task:
    """Cancel task.
    
    Args:
        task_id: Task to cancel
    
    Returns:
        Cancelled task
    """
    pass


async def retry_task(task_id: str) -> Task:
    """Retry failed task.
    
    Args:
        task_id: Task to retry
    
    Returns:
        Task in pending state
    """
    pass


# ── Helper functions for serialization/deserialization ──────────────────────

def _deserialize_task_scope(payload: dict) -> TaskScope:
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
