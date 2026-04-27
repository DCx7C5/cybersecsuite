"""PlanManager: CRUD and lifecycle for Plans and Tasks."""
from typing import List

from db.models.plan import ExecutionLog, Plan, Task


class PlanManager:
    async def create_plan(self, title: str, description: str = "", scope: str = "general") -> Plan:
        return await Plan.create(title=title, description=description, scope=scope)

    async def add_task(self, plan_id: int, title: str, description: str = "") -> Task:
        plan = await Plan.get(id=plan_id)
        return await Task.create(plan=plan, title=title, description=description)

    async def add_dependency(self, task_id: int, depends_on_id: int) -> None:
        task = await Task.get(id=task_id).prefetch_related("depends_on")
        dep = await Task.get(id=depends_on_id)
        await task.depends_on.add(dep)

    async def get_ready_tasks(self, plan_id: int) -> List[Task]:
        """Return pending tasks whose dependencies are all done."""
        tasks = await Task.filter(plan_id=plan_id, status="pending").prefetch_related("depends_on")
        return [t for t in tasks if all(d.status == "done" for d in t.depends_on)]

    async def set_task_status(self, task_id: int, status: str) -> Task:
        task = await Task.get(id=task_id)
        task.status = status
        await task.save()
        return task

    async def log(self, task_id: int, message: str, level: str = "info") -> ExecutionLog:
        task = await Task.get(id=task_id)
        return await ExecutionLog.create(task=task, message=message, level=level)

    async def get_plan_summary(self, plan_id: int) -> dict:
        plan = await Plan.get(id=plan_id)
        tasks = await Task.filter(plan_id=plan_id)
        by_status: dict[str, int] = {}
        for t in tasks:
            by_status[t.status] = by_status.get(t.status, 0) + 1
        return {"id": plan.id, "title": plan.title, "status": plan.status, "tasks": by_status}
