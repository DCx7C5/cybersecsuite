"""PlanManager: CRUD and lifecycle for Plans, Tasks, and Todos."""
import logging
from datetime import datetime
from typing import List, Optional

from db.models.plan import Plan, Task, Todo

logger = logging.getLogger(__name__)


class PlanManager:
    async def create_plan(self, title: str, description: str = "", scope: str = "general") -> Plan:
        """Create a new plan."""
        return await Plan.create(title=title, description=description, scope=scope)

    async def add_task(
        self,
        plan_id: int,
        title: str,
        description: str = "",
        assigned_to: str = None,
        sequence: int = 0,
        target_files: Optional[List[str]] = None,
    ) -> Task:
        """Add a task to a plan."""
        plan = await Plan.get(id=plan_id)
        task = await Task.create(
            plan=plan,
            title=title,
            description=description,
            assigned_to=assigned_to,
            sequence=sequence,
        )
        if target_files:
            task.set_target_files(target_files)
            await task.save()
        return task

    async def add_todo(self, task_id: int, content: str, assignee: str = None) -> Todo:
        """Add a todo (sub-task) to a task."""
        task = await Task.get(id=task_id)
        return await Todo.create(task=task, content=content, assignee=assignee)

    async def add_dependency(self, task_id: int, depends_on_id: int, validate_dag: bool = True) -> bool:
        """
        Add a task dependency with optional cycle detection.
        
        Args:
            task_id: Task that will depend on another
            depends_on_id: Task that must be completed first
            validate_dag: If True, check for cycles before adding dependency
            
        Returns:
            True if dependency added successfully
            
        Raises:
            ValueError: If self-dependency, cross-plan dependency, or cycle detected
        """
        if task_id == depends_on_id:
            raise ValueError("Task cannot depend on itself")
        
        task = await Task.get(id=task_id).prefetch_related("depends_on")
        dep = await Task.get(id=depends_on_id)
        
        if task.plan_id != dep.plan_id:
            raise ValueError("Cross-plan dependencies not allowed")
        
        if validate_dag and await self._would_create_cycle(task_id, depends_on_id):
            raise ValueError("Adding this dependency would create a cycle")
        
        await task.depends_on.add(dep)
        return True

    async def _would_create_cycle(self, task_id: int, new_dep_id: int, memo: dict = None) -> bool:
        """
        Check if adding a dependency (task_id depends on new_dep_id) would create a cycle.
        Uses DFS with memoization to detect cycles.
        
        A cycle exists if new_dep_id depends (directly or transitively) on task_id.
        """
        if memo is None:
            memo = {}
        
        visited = set()
        
        async def has_path_to_target(current_id: int, target_id: int) -> bool:
            if current_id == target_id:
                return True
            if current_id in visited:
                return False
            if current_id in memo:
                return memo[current_id]
            
            visited.add(current_id)
            current_task = await Task.get(id=current_id).prefetch_related("depends_on")
            
            for dep in current_task.depends_on:
                if await has_path_to_target(dep.id, target_id):
                    return True
            
            result = False
            memo[current_id] = result
            return result
        
        return await has_path_to_target(new_dep_id, task_id)

    async def validate_plan_dag(self, plan_id: int) -> List[str]:
        """
        Validate that all tasks in a plan form a valid DAG (no cycles).
        
        Returns:
            List of error messages (empty if valid DAG)
        """
        errors = []
        tasks = await Task.filter(plan_id=plan_id).prefetch_related("depends_on")
        
        for task in tasks:
            visited = set()
            
            async def has_cycle_from(current_id: int) -> bool:
                if current_id in visited:
                    return True
                visited.add(current_id)
                current_task = await Task.get(id=current_id).prefetch_related("depends_on")
                for dep in current_task.depends_on:
                    if await has_cycle_from(dep.id):
                        return True
                visited.discard(current_id)
                return False
            
            if await has_cycle_from(task.id):
                errors.append(f"Cycle detected involving task {task.id} ({task.title})")
        
        return errors

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

    async def delegate_task_with_hooks(
        self,
        task_id: int,
        agent_name: str,
        session_id: str,
        dry_run: bool = True,
    ) -> bool:
        """
        Delegate a task to an agent with hook support.
        Calls agent hooks (start/stop) with target_files support.
        
        Args:
            task_id: Task to delegate
            agent_name: Agent handling the task
            session_id: Session ID
            dry_run: If True, ruff runs in dry-run mode
            
        Returns:
            True if delegation was successful
        """
        try:
            task = await Task.get(id=task_id)
            target_files = task.get_target_files()
            
            # Import hooks here to avoid circular imports
            from hooks.agent_hooks import on_agent_start, on_agent_stop
            
            # Call agent start hook
            logger.info(f"Starting agent {agent_name} for task {task_id} with {len(target_files)} target files")
            await on_agent_start(agent_name, session_id, target_files)
            
            # Delegate work (placeholder - actual delegation happens in calling code)
            # ...
            
            # Call agent stop hook
            logger.info(f"Stopping agent {agent_name} for task {task_id}")
            await on_agent_stop(agent_name, session_id, target_files, dry_run=dry_run)
            
            return True
        except Exception as e:
            logger.error(f"Failed to delegate task {task_id}: {e}")
            return False

    
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
