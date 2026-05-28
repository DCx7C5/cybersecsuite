"""Task types — immutable scope + mutable state machine."""
import msgspec

from datetime import datetime
from typing import Any

from css.core.base.workflow import BaseTask, BaseTaskScope
from css.core.query import Query
from .enums import TaskStatus, TaskPriority


class TaskScope(BaseTaskScope):
    """Immutable task snapshot (read-only context)."""

    team_id: int = 0
    orchestrator_id: str = ""
    query: Query = msgspec.field(default_factory=lambda: None)  # type: ignore[arg-type]
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    timeout_seconds: int = 300
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "id": self.id,
            "team_id": self.team_id,
            "orchestrator_id": self.orchestrator_id,
            "query": self.query.to_dict(),
            "priority": self.priority.value,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "metadata": self.metadata,
        }

class Task(BaseTask):
    """Mutable task state machine."""

    scope: TaskScope = msgspec.field(default_factory=TaskScope)
    status: TaskStatus = TaskStatus.PENDING
    assigned_member_id: str | None = None
    assigned_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    retry_count: int = 0
    result: object | None = None
    error: str | None = None
    
    def can_execute(self) -> bool:
        """Check if task can be executed."""
        return self.status in (TaskStatus.PENDING, TaskStatus.PAUSED)
    
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return (
            self.status == TaskStatus.FAILED
            and self.retry_count < self.scope.max_retries
        )
    
    def can_cancel(self) -> bool:
        """Check if task can be cancelled."""
        return self.status in (TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.PAUSED)
    
    def can_pause(self) -> bool:
        """Check if task can be paused."""
        return self.status == TaskStatus.EXECUTING
    
    def mark_queued(self) -> None:
        """Transition to queued."""
        if self.status != TaskStatus.PENDING:
            raise RuntimeError(f"Cannot queue task in {self.status} state")
        self.status = TaskStatus.QUEUED
    
    def mark_executing(self, member_id: str) -> None:
        """Transition to executing."""
        if self.status not in (TaskStatus.QUEUED, TaskStatus.PAUSED):
            raise RuntimeError(f"Cannot execute task in {self.status} state")
        self.status = TaskStatus.EXECUTING
        self.assigned_member_id = member_id
        self.assigned_at = datetime.now()
        self.started_at = datetime.now()
    
    def mark_completed(self, result: Any) -> None:
        """Transition to completed."""
        if self.status != TaskStatus.EXECUTING:
            raise RuntimeError(f"Cannot complete task in {self.status} state")
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()
    
    def mark_failed(self, error: str) -> None:
        """Transition to failed."""
        if self.status != TaskStatus.EXECUTING:
            raise RuntimeError(f"Cannot fail task in {self.status} state")
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()
        self.retry_count += 1
    
    def mark_paused(self) -> None:
        """Transition to paused."""
        if self.status != TaskStatus.EXECUTING:
            raise RuntimeError(f"Cannot pause task in {self.status} state")
        self.status = TaskStatus.PAUSED
    
    def mark_cancelled(self) -> None:
        """Transition to cancelled."""
        if not self.can_cancel():
            raise RuntimeError(f"Cannot cancel task in {self.status} state")
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "id": self.id,
            "scope": self.scope.to_dict(),
            "status": self.status.value,
            "assigned_member_id": self.assigned_member_id,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "result": self.result,
            "error": self.error,
        }
