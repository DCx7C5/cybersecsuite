"""A2A Task persistence model — stores agent tasks in PostgreSQL via Tortoise ORM."""
from tortoise import fields
from tortoise.models import Model


class A2ATask(Model):
    """Persisted A2A task for durability and cross-session queries."""
    id = fields.BigIntField(max_length=128, pk=True)
    session_id = fields.CharField(max_length=128, null=True, db_index=True)
    state = fields.CharField(max_length=32, default="submitted", db_index=True)
    history = fields.JSONField(default=list)
    artifacts = fields.JSONField(default=list)
    metadata = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "a2a_tasks"
        table_description_plural = "A2A Tasks"
        table_description_singular = "A2A Task"
        ordering = ["-updated_at"]
        indexes = [
            ("session_id", "state"),
        ]
        unique_together = (("session_id", "id"),)

