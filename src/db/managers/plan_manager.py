"""PlanManager: CRUD and lifecycle for Plans, Tasks, and Todos."""
from datetime import datetime
from typing import List

from db.models.plan import Plan, Task, Todo


class PlanManager:
    async def create_plan(self, title: str, description: str = "", scope: str = "general") -> Plan:
        """Create a new plan."""
        return await Plan.create(title=title, description=description, scope=scope)

    async def add_task(self, plan_id: int, title: str, description: str = "", assigned_to: str = None, sequence: int = 0) -> Task:
        """Add a task to a plan."""
        plan = await Plan.get(id=plan_id)
        return await Task.create(plan=plan, title=title, description=description, assigned_to=assigned_to, sequence=sequence)

    async def add_todo(self, task_id: int, content: str, assignee: str = None) -> Todo:
        """Add a todo (sub-task) to a task."""
        task = await Task.get(id=task_id)
        return await Todo.create(task=task, content=content, assignee=assignee)

    async def add_dependency(self, task_id: int, depends_on_id: int) -> None:
        """Add a task dependency."""
        task = await Task.get(id=task_id).prefetch_related("depends_on")
        dep = await Task.get(id=depends_on_id)
        await task.depends_on.add(dep)

    async def get_ready_tasks(self, plan_id: int) -> List[Task]:
        """Return pending tasks whose dependencies are all done and not claimed."""
        tasks = await Task.filter(plan_id=plan_id, status="pending", claimed_by="").prefetch_related("depends_on")
        return [t for t in tasks if all(d.status == "done" for d in t.depends_on)]

    async def get_plan_tasks(self, plan_id: int) -> List[Task]:
        """Get all tasks for a plan, ordered by sequence."""
        return await Task.filter(plan_id=plan_id).order_by("sequence")

    async def get_plan_hierarchy(self, plan_id: int) -> dict:
        """Get plan with all tasks and todos, including dependency graph."""
        plan = await Plan.get(id=plan_id)
        tasks = await Task.filter(plan_id=plan_id).order_by("sequence").prefetch_related("todos", "depends_on")
        return {
            "plan": plan,
            "tasks": [
                {
                    "task": t,
                    "todos": await t.todos.all(),
                    "depends_on": list(t.depends_on),
                }
                for t in tasks
            ],
        }

    async def set_task_status(self, task_id: int, status: str) -> Task:
        """Update task status and clear claimed_by when transitioning to terminal states."""
        task = await Task.get(id=task_id)
        task.status = status
        # Clear claim when task is done or blocked
        if status in ("done", "blocked"):
            task.claimed_by = ""
            task.claimed_at = None
            task.lease_expires_at = None
        await task.save()
        return task

    async def claim_task(self, task_id: int, claimed_by: str, lease_expires_at: datetime | None = None) -> bool:
        """
        Atomically claim a task if it's pending and not already claimed.
        Returns True if claim succeeds, False if already claimed or not pending.
        """
        task = await Task.get(id=task_id)
        if task.status != "pending" or task.claimed_by != "":
            return False  # already claimed or not pending
        task.claimed_by = claimed_by
        task.claimed_at = datetime.now()
        task.lease_expires_at = lease_expires_at
        task.status = "in_progress"
        await task.save()
        return True

    async def cleanup_expired_leases(self, lease_timeout_minutes: int = 60) -> int:
        """
        Find tasks with expired leases and reset claimed_by.
        Returns count of tasks reset.
        """
        now = datetime.now()
        expired_tasks = await Task.filter(
            lease_expires_at__lt=now
        ).exclude(claimed_by="")
        count = 0
        for task in expired_tasks:
            task.claimed_by = ""
            task.claimed_at = None
            task.lease_expires_at = None
            task.status = "pending"
            await task.save()
            count += 1
        return count

    
    async def set_todo_status(self, todo_id: int, status: str) -> Todo:
        """Update todo status."""
        todo = await Todo.get(id=todo_id)
        todo.status = status
        await todo.save()
        return todo

    async def get_plan_summary(self, plan_id: int) -> dict:
        """Get plan summary with task and todo status counts."""
        plan = await Plan.get(id=plan_id)
        tasks = await Task.filter(plan_id=plan_id)
        todos = []
        for t in tasks:
            todos.extend(await t.todos.all())

        task_by_status: dict[str, int] = {}
        for t in tasks:
            task_by_status[t.status] = task_by_status.get(t.status, 0) + 1

        todo_by_status: dict[str, int] = {}
        for t in todos:
            todo_by_status[t.status] = todo_by_status.get(t.status, 0) + 1

        return {
            "id": plan.id,
            "title": plan.title,
            "status": plan.status,
            "tasks": task_by_status,
            "todos": todo_by_status,
        }
