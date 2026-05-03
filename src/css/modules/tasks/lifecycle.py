"""Task lifecycle management — state transitions + validation."""

from typing import Optional

from .enums import TaskStatus
from .types import Task


class TaskLifecycle:
    """Task state machine manager."""
    
    @staticmethod
    def validate_transition(current_status: TaskStatus, target_status: TaskStatus) -> bool:
        """Validate state transition.
        
        Valid transitions:
        - PENDING → QUEUED
        - QUEUED → EXECUTING
        - EXECUTING → COMPLETED
        - EXECUTING → FAILED
        - EXECUTING → PAUSED
        - PAUSED → EXECUTING
        - PENDING/QUEUED/PAUSED → CANCELLED
        - FAILED → QUEUED (retry)
        """
        transitions = {
            TaskStatus.PENDING: {TaskStatus.QUEUED, TaskStatus.CANCELLED},
            TaskStatus.QUEUED: {TaskStatus.EXECUTING, TaskStatus.CANCELLED},
            TaskStatus.EXECUTING: {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.PAUSED},
            TaskStatus.PAUSED: {TaskStatus.EXECUTING, TaskStatus.CANCELLED},
            TaskStatus.FAILED: {TaskStatus.QUEUED},  # Retry
            TaskStatus.COMPLETED: set(),  # Terminal
            TaskStatus.CANCELLED: set(),  # Terminal
        }
        return target_status in transitions.get(current_status, set())
    
    @staticmethod
    async def queue_task(task: Task) -> None:
        """Transition task to queued."""
        if not TaskLifecycle.validate_transition(task.status, TaskStatus.QUEUED):
            raise RuntimeError(
                f"Cannot transition from {task.status} to QUEUED"
            )
        task.mark_queued()
    
    @staticmethod
    async def execute_task(task: Task, member_id: str) -> None:
        """Transition task to executing."""
        if not TaskLifecycle.validate_transition(task.status, TaskStatus.EXECUTING):
            raise RuntimeError(
                f"Cannot transition from {task.status} to EXECUTING"
            )
        task.mark_executing(member_id)
    
    @staticmethod
    async def complete_task(task: Task, result: any) -> None:
        """Transition task to completed."""
        if not TaskLifecycle.validate_transition(task.status, TaskStatus.COMPLETED):
            raise RuntimeError(
                f"Cannot transition from {task.status} to COMPLETED"
            )
        task.mark_completed(result)
    
    @staticmethod
    async def fail_task(task: Task, error: str) -> None:
        """Transition task to failed."""
        if not TaskLifecycle.validate_transition(task.status, TaskStatus.FAILED):
            raise RuntimeError(
                f"Cannot transition from {task.status} to FAILED"
            )
        task.mark_failed(error)
    
    @staticmethod
    async def pause_task(task: Task) -> None:
        """Transition task to paused."""
        if not TaskLifecycle.validate_transition(task.status, TaskStatus.PAUSED):
            raise RuntimeError(
                f"Cannot transition from {task.status} to PAUSED"
            )
        task.mark_paused()
    
    @staticmethod
    async def cancel_task(task: Task) -> None:
        """Transition task to cancelled."""
        if not TaskLifecycle.validate_transition(task.status, TaskStatus.CANCELLED):
            raise RuntimeError(
                f"Cannot transition from {task.status} to CANCELLED"
            )
        task.mark_cancelled()
    
    @staticmethod
    async def retry_task(task: Task) -> None:
        """Transition failed task back to queued for retry."""
        if not task.can_retry():
            raise RuntimeError(
                f"Cannot retry task in {task.status} state "
                f"(retries: {task.retry_count}/{task.scope.max_retries})"
            )
        if not TaskLifecycle.validate_transition(task.status, TaskStatus.QUEUED):
            raise RuntimeError(
                f"Cannot transition from {task.status} to QUEUED for retry"
            )
        task.status = TaskStatus.QUEUED
        task.assigned_member_id = None
        task.assigned_at = None


__all__ = ["TaskLifecycle"]
