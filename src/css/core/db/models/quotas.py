"""Task assignment, team quota, and task result models."""

from datetime import datetime

import msgspec
from tortoise import fields, models
from css.core.db.models.base import BaseModel
from .enums import TaskAssignmentStatus, TaskPriority


class TaskAssignmentInfo(msgspec.Struct):
    """Domain value type for task assignment data."""
    id: int
    team_id: int
    orchestrator_id: int
    task_id: str
    status: str
    priority: str
    timeout_seconds: int
    retry_count: int
    max_retries: int
    task_payload: dict | None
    assigned_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    assigned_member_id: str | None


class TaskAssignment(BaseModel):
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
    updated_at = fields.DatetimeField(auto_now=True)
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    assigned_member_id = fields.CharField(max_length=256, null=True)

    def to_domain(self) -> TaskAssignmentInfo:
        return TaskAssignmentInfo(
            id=self.id,
            team_id=self.team_id,
            orchestrator_id=self.orchestrator_id,
            task_id=self.task_id,
            status=self.status.value if hasattr(self.status, 'value') else self.status,
            priority=self.priority.value if hasattr(self.priority, 'value') else self.priority,
            timeout_seconds=self.timeout_seconds,
            retry_count=self.retry_count,
            max_retries=self.max_retries,
            task_payload=self.task_payload,
            assigned_at=self.assigned_at,
            updated_at=self.updated_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            assigned_member_id=self.assigned_member_id,
        )

    @classmethod
    def from_domain(cls, info: TaskAssignmentInfo) -> "TaskAssignment":
        return cls(
            team_id=info.team_id,
            orchestrator_id=info.orchestrator_id,
            task_id=info.task_id,
            status=info.status,
            priority=info.priority,
            timeout_seconds=info.timeout_seconds,
            retry_count=info.retry_count,
            max_retries=info.max_retries,
            task_payload=info.task_payload,
            started_at=info.started_at,
            completed_at=info.completed_at,
            assigned_member_id=info.assigned_member_id,
        )

    class Meta:
        table = "task_assignments"
        indexes = [
            models.Index(fields=["team_id", "status"]),
            models.Index(fields=["orchestrator_id", "status"]),
            models.Index(fields=["task_id"]),
        ]


class TaskResult(BaseModel):
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


class TeamQuotaInfo(msgspec.Struct):
    """Domain value type for team quota data."""
    id: int
    team_id: int
    max_concurrent_tasks: int
    max_daily_tasks: int
    cpu_quota_percent: float
    memory_quota_mb: int
    current_concurrent_tasks: int
    daily_tasks_count: int
    daily_reset_at: datetime | None


class TeamQuota(BaseModel):
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
    daily_reset_at = fields.DatetimeField(null=True)

    def to_domain(self) -> TeamQuotaInfo:
        return TeamQuotaInfo(
            id=self.id,
            team_id=self.team_id,
            max_concurrent_tasks=self.max_concurrent_tasks,
            max_daily_tasks=self.max_daily_tasks,
            cpu_quota_percent=self.cpu_quota_percent,
            memory_quota_mb=self.memory_quota_mb,
            current_concurrent_tasks=self.current_concurrent_tasks,
            daily_tasks_count=self.daily_tasks_count,
            daily_reset_at=self.daily_reset_at,
        )

    @classmethod
    def from_domain(cls, info: TeamQuotaInfo) -> "TeamQuota":
        return cls(
            team_id=info.team_id,
            max_concurrent_tasks=info.max_concurrent_tasks,
            max_daily_tasks=info.max_daily_tasks,
            cpu_quota_percent=info.cpu_quota_percent,
            memory_quota_mb=info.memory_quota_mb,
            current_concurrent_tasks=info.current_concurrent_tasks,
            daily_tasks_count=info.daily_tasks_count,
            daily_reset_at=info.daily_reset_at,
        )

    class Meta:
        table = "team_quotas"
        indexes = [
            models.Index(fields=["team_id"]),
        ]
