"""A2A tasks CRUD — dedicated route module (re-exports from ops)."""
from dashboard.api.ops import (
    api_tasks_list as api_a2a_tasks_list,
    api_tasks_create as api_a2a_tasks_create,
    api_tasks_update as api_a2a_tasks_update,
    api_tasks_delete as api_a2a_tasks_delete,
)

__all__ = [
    "api_a2a_tasks_list",
    "api_a2a_tasks_create",
    "api_a2a_tasks_update",
    "api_a2a_tasks_delete",
]
