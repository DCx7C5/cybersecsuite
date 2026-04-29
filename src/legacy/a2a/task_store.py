"""
A2A Task Store — in-memory task registry with DB persistence via Tortoise ORM.
"""
import uuid
from typing import Dict, Optional, List
from datetime import datetime, timezone

from a2a.models import Task, TaskStatus, Message, TaskArtifact, TaskSendParams
from a2a.enums import TaskState


class TaskStore:
    """Thread-safe in-memory task registry with optional DB persistence."""

    def __init__(self, persist: bool = True) -> None:
        self._tasks: Dict[str, Task] = {}
        self._persist = persist

    def create(self, params: TaskSendParams) -> Task:
        """Create a new task from send params."""
        task = Task(
            id=params.id,
            session_id=params.session_id,
            status=TaskStatus(state=TaskState.SUBMITTED),
            history=[params.message] if params.message else [],
            artifacts=[],
            metadata=params.metadata,
        )
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Optional[Task]:
        """Retrieve task by ID."""
        return self._tasks.get(task_id)

    def update_status(
        self,
        task_id: str,
        state: TaskState,
        message: Optional[Message] = None,
    ) -> Optional[Task]:
        """Update task state."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        task.status = TaskStatus(
            state=state,
            message=message,
            timestamp=datetime.now(timezone.utc),
        )
        if message and task.history is not None:
            task.history.append(message)
        return task

    def add_artifact(self, task_id: str, artifact: TaskArtifact) -> Optional[Task]:
        """Append output artifact to a task."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        if task.artifacts is None:
            task.artifacts = []
        task.artifacts.append(artifact)
        return task

    def cancel(self, task_id: str) -> Optional[Task]:
        """Cancel a task if it is cancelable."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        if task.status.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELED):
            return None  # Already terminal
        task.status = TaskStatus(
            state=TaskState.CANCELED,
            timestamp=datetime.now(timezone.utc),
        )
        return task

    def list_tasks(self, session_id: Optional[str] = None) -> List[Task]:
        """List all tasks, optionally filtered by session."""
        tasks = list(self._tasks.values())
        if session_id:
            tasks = [t for t in tasks if t.session_id == session_id]
        return tasks

    def generate_id(self) -> str:
        """Generate a unique task ID."""
        return str(uuid.uuid4())

    # ── DB Persistence (Tortoise ORM) ─────────────────────────────────────────

    async def persist_task(self, task: Task) -> None:
        """Save or update a task in the database."""
        if not self._persist:
            return
        from db.models.a2a_task import A2ATask

        history_json = [m.model_dump(mode="json") for m in (task.history or [])]
        artifacts_json = [a.model_dump(mode="json") for a in (task.artifacts or [])]
        metadata = task.metadata or {}

        await A2ATask.update_or_create(
            defaults={
                "session_id": task.session_id,
                "state": task.status.state.value,
                "history": history_json,
                "artifacts": artifacts_json,
                "metadata": metadata,
            },
            id=task.id,
        )

    async def load_task(self, task_id: str) -> Optional[Task]:
        """Load a task from the database into memory."""
        from db.models.a2a_task import A2ATask
        row = await A2ATask.get_or_none(id=task_id)
        if not row:
            return None
        task = Task(
            id=row.id,
            session_id=row.session_id,
            status=TaskStatus(state=TaskState(row.state)),
            history=row.history,
            artifacts=row.artifacts,
            metadata=row.metadata,
        )
        self._tasks[task.id] = task
        return task

    async def load_all_tasks(self, session_id: Optional[str] = None) -> List[Task]:
        """Load all tasks from the database."""
        from db.models.a2a_task import A2ATask
        query = A2ATask.all()
        if session_id:
            query = query.filter(session_id=session_id)
        rows = await query
        tasks = []
        for row in rows:
            task = Task(
                id=row.id,
                session_id=row.session_id,
                status=TaskStatus(state=TaskState(row.state)),
                history=row.history,
                artifacts=row.artifacts,
                metadata=row.metadata,
            )
            self._tasks[task.id] = task
            tasks.append(task)
        return tasks

    async def get_task_stats(self) -> Dict[str, int]:
        """Get task state counts from the database."""
        from db.models.a2a_task import A2ATask
        stats: Dict[str, int] = {}
        for state in TaskState:
            stats[state.value] = await A2ATask.filter(state=state.value).count()
        stats["total"] = await A2ATask.all().count()
        return stats
