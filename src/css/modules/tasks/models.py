"""Module auto-discovery stub; canonical task ORM ownership is in core DB models."""

from css.core.db.models.tasks import TaskAssignment, TaskResult

tortoise_models = [TaskAssignment, TaskResult]
