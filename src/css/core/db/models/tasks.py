"""Canonical task lifecycle ORM models: TaskAssignment and TaskResult."""

from datetime import datetime
from typing import cast

import msgspec
from tortoise import fields
from tortoise.indexes import Index

from css.core.db.serializers import BaseModelSerializer
from .base import BaseModel
from .enums import TaskAssignmentStatus, TaskPriority


class TaskAssignmentInfo(msgspec.Struct, frozen=True, kw_only=True):
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
    task_payload: dict[str, object] | None
    assigned_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    assigned_member_id: str | None


class TaskResultInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for task result data."""

    id: int
    task_assignment_id: int
    result_text: str | None
    result_metadata: dict[str, object] | None
    error_message: str | None
    execution_time_ms: int | None
    created_at: datetime


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
        team_id = cast(int, getattr(self, "team_id"))
        return TaskAssignmentInfo(
            id=self.id,
            team_id=team_id,
            orchestrator_id=self.orchestrator_id,
            task_id=self.task_id,
            status=self.status.value if hasattr(self.status, 'value') else self.status,
            priority=self.priority.value if hasattr(self.priority, 'value') else self.priority,
            timeout_seconds=self.timeout_seconds,
            retry_count=self.retry_count,
            max_retries=self.max_retries,
            task_payload=dict(self.task_payload or {}) if self.task_payload else None,
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

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "task_assignments"
        table_verbose = "Task Assignment"
        table_verbose_plural = "Task Assignments"
        indexes = [
            Index(fields=["team_id", "status"]),
            Index(fields=["orchestrator_id", "status"]),
            Index(fields=["task_id"]),
        ]


class TaskResult(BaseModel):
    """Task execution result storage."""
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

    def to_domain(self) -> TaskResultInfo:
        task_assignment_id = cast(int, getattr(self, "task_assignment_id"))
        return TaskResultInfo(
            id=self.id,
            task_assignment_id=task_assignment_id,
            result_text=self.result_text,
            result_metadata=dict(self.result_metadata or {}) if self.result_metadata else None,
            error_message=self.error_message,
            execution_time_ms=self.execution_time_ms,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, info: TaskResultInfo) -> "TaskResult":
        return cls(
            task_assignment_id=info.task_assignment_id,
            result_text=info.result_text,
            result_metadata=dict(info.result_metadata) if info.result_metadata else None,
            error_message=info.error_message,
            execution_time_ms=info.execution_time_ms,
            created_at=info.created_at,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "task_results"
        table_verbose = "Task Result"
        table_verbose_plural = "Task Results"
        indexes = [
            Index(fields=["task_assignment_id"]),
        ]

class TaskAssignmentSerializer(BaseModelSerializer[TaskAssignment]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = TaskAssignment
        fields = "__all__"
        read_only_fields = ("id", "assigned_at", "updated_at")


class TaskResultSerializer(BaseModelSerializer[TaskResult]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = TaskResult
        fields = "__all__"
        read_only_fields = ("id", "created_at")
