from datetime import datetime

import msgspec
from tortoise.fields import (
    BigIntField,
    ForeignKeyField,
    CASCADE,
    CharField,
    CharEnumField,
    IntField,
    JSONField,
    DatetimeField,
    OneToOneField,
    TextField,
)
from tortoise.indexes import Index

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
    task_payload: dict | None
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
    result_metadata: dict | None
    error_message: str | None
    execution_time_ms: int | None
    created_at: datetime


class TaskAssignment(BaseModel):
    """Task assignment tracking with team isolation."""
    id = BigIntField(primary_key=True)
    team = ForeignKeyField(
        "models.Team",
        related_name="task_assignments",
        on_delete=CASCADE,
        db_index=True,
    )
    orchestrator_id = BigIntField(db_index=True)
    task_id = CharField(max_length=256, db_index=True, unique=True)
    status = CharEnumField(
        TaskAssignmentStatus,
        default=TaskAssignmentStatus.PENDING,
        db_index=True,
    )
    priority = CharEnumField(
        TaskPriority,
        default=TaskPriority.NORMAL,
    )
    timeout_seconds = IntField(default=300)
    retry_count = IntField(default=0)
    max_retries = IntField(default=3)
    task_payload = JSONField(
        null=True,
        description="Full task data (Query, metadata, etc.) for deserialization",
    )
    assigned_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)
    started_at = DatetimeField(null=True)
    completed_at = DatetimeField(null=True)
    assigned_member_id = CharField(max_length=256, null=True)

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
    task_assignment = OneToOneField(
        "models.TaskAssignment",
        related_name="result",
        on_delete=CASCADE,
    )
    result_text = TextField(null=True)
    result_metadata = JSONField(null=True)
    error_message = TextField(null=True)
    execution_time_ms = IntField(null=True)
    created_at = DatetimeField(auto_now_add=True)

    def to_domain(self) -> TaskResultInfo:
        return TaskResultInfo(
            id=self.id,
            task_assignment_id=self.task_assignment_id,
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
