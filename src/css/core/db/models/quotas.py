"""Task assignment and team quota models."""

from tortoise import fields, models


class TaskAssignment(models.Model):
    """Task assignment tracking with team isolation."""
    id = fields.BigIntField(primary_key=True)
    team = fields.ForeignKeyField(
        "models.Team",
        related_name="task_assignments",
        on_delete=fields.CASCADE,
        db_index=True,
    )
    orchestrator_id = fields.BigIntField(db_index=True)
    task_id = fields.CharField(max_length=256, db_index=True)
    status = fields.CharField(
        max_length=32,
        default="pending",
        db_index=True,
    )
    assigned_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "task_assignments"
        indexes = [
            models.Index(fields=["team_id", "status"]),
            models.Index(fields=["orchestrator_id", "status"]),
        ]


class TeamQuota(models.Model):
    """Team resource quotas enforcement."""
    id = fields.BigIntField(primary_key=True)
    team = fields.OneToOneField(
        "models.Team",
        related_name="quota",
        on_delete=fields.CASCADE,
    )
    max_concurrent_tasks = fields.IntField(default=50)
    max_daily_tasks = fields.IntField(default=500)
    cpu_quota_percent = fields.FloatField(default=100.0)
    memory_quota_mb = fields.IntField(default=2048)
    current_concurrent_tasks = fields.IntField(default=0)
    daily_tasks_count = fields.IntField(default=0)
    daily_reset_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "team_quotas"
        indexes = [
            models.Index(fields=["team_id"]),
        ]
