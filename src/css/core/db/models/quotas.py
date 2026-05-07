"""Task assignment, team quota, and task result models."""

from tortoise import fields, models
from .enums import TaskAssignmentStatus, TaskPriority


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
    task_id = fields.CharField(max_length=256, db_index=True, unique=True)
    status = fields.CharEnumField(
        TaskAssignmentStatus,
        default=TaskAssignmentStatus.PENDING,
        db_index=True,
    )
    priority = fields.CharEnumField(
        TaskPriority,
        default=TaskPriority.NORMAL,
    )
    timeout_seconds = fields.IntField(default=300)
    retry_count = fields.IntField(default=0)
    max_retries = fields.IntField(default=3)
    task_payload = fields.JSONField(
        null=True,
        description="Full task data (Query, metadata, etc.) for deserialization",
    )
    assigned_at = fields.DatetimeField(auto_now_add=True)
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    assigned_member_id = fields.CharField(max_length=256, null=True)

    class Meta:
        table = "task_assignments"
        indexes = [
            models.Index(fields=["team_id", "status"]),
            models.Index(fields=["orchestrator_id", "status"]),
            models.Index(fields=["task_id"]),
        ]


class TaskResult(models.Model):
    """Task execution result storage."""
    id = fields.BigIntField(primary_key=True)
    task_assignment = fields.OneToOneField(
        "models.TaskAssignment",
        related_name="result",
        on_delete=fields.CASCADE,
    )
    result_text = fields.TextField(null=True)
    result_metadata = fields.JSONField(null=True)
    error_message = fields.TextField(null=True)
    execution_time_ms = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "task_results"
        indexes = [
            models.Index(fields=["task_assignment_id"]),
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
