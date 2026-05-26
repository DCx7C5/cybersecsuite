"""Task module — ORM models live in css.core.db.models.tasks."""

from css.core.db.models.tasks import TaskAssignment, TaskResult

tortoise_models = [TaskAssignment, TaskResult]
