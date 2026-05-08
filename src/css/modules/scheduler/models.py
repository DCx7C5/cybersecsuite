"""Scheduler module — cron-based task execution (Phase 7)."""

from tortoise import fields
from datetime import datetime

from css.core.db.models.base import BaseModel
from .enums import TaskType


class ScheduledTask(BaseModel):
    """Cron-scheduled task."""
    
    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="scheduled_tasks",
        on_delete=fields.CASCADE,
    )
    
    # Task definition
    task_id = fields.CharField(max_length=128, db_index=True)
    task_type = fields.CharField(
        max_length=32,
        choices=[t.value for t in TaskType],
        db_index=True,
    )
    
    name = fields.CharField(max_length=256)
    description = fields.TextField(default="")
    
    # Schedule
    cron_expression = fields.CharField(
        max_length=128,
        help_text="Cron format: '0 2 * * *' for 2 AM daily"
    )
    timezone = fields.CharField(max_length=64, default="UTC")
    
    # Configuration
    task_config = fields.JSONField(
        default=dict,
        help_text="Task-specific config (scan_type, feed_id, etc.)"
    )
    
    # Status
    is_active = fields.BooleanField(default=True, db_index=True)
    
    # Tracking
    last_run_at = fields.DatetimeField(null=True)
    last_run_status = fields.CharField(
        max_length=32,
        null=True,
        choices=["success", "failed", "running"],
    )
    next_run_at = fields.DatetimeField(null=True)
    
    # Metadata
    created_by = fields.CharField(max_length=255, default="system")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "scheduled_tasks"
        unique_together = (("organization", "task_id"),)


class TaskExecution(BaseModel):
    """Record of task execution."""
    
    id = fields.BigIntField(primary_key=True)
    task: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.ScheduledTask",
        related_name="executions",
        on_delete=fields.CASCADE,
    )
    
    # Execution details
    status = fields.CharField(
        max_length=32,
        choices=["success", "failed", "partial"],
        db_index=True,
    )
    
    started_at = fields.DatetimeField()
    completed_at = fields.DatetimeField()
    
    # Results
    output = fields.TextField(default="")
    error_message = fields.TextField(default="")
    
    # Metrics
    duration_seconds = fields.FloatField()
    
    class Meta:
        table = "task_executions"
        ordering = ["-completed_at"]


__all__ = [
    "TaskType",
    "ScheduledTask",
    "TaskExecution",
]
