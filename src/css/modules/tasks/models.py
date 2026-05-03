"""Task module integration — auto-discovery loader."""

# Import from submodules (auto-discovery pattern)
from .enums import TaskPriority, TaskRoutingStrategy, TaskStatus
from .types import Task, TaskScope
from .endpoints import (
    cancel_task,
    create_task,
    get_task,
    list_tasks,
    retry_task,
    update_task_status,
)

__all__ = [
    # Enums
    "TaskStatus",
    "TaskPriority",
    "TaskRoutingStrategy",
    # Types
    "Task",
    "TaskScope",
    # Endpoints
    "create_task",
    "get_task",
    "list_tasks",
    "update_task_status",
    "cancel_task",
    "retry_task",
]
