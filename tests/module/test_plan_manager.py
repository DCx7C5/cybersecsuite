"""Tests for PlanManager: CRUD, ready-task logic, dependency gating, and todo management."""
from __future__ import annotations

import sys

import pytest
from tortoise.context import TortoiseContext

_SKIP_TORTOISE = pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Tortoise ORM SQLite backend incompatible with Python 3.14",
)

_PLAN_MODELS = [
    "db.models.plan",
]


@pytest.fixture
async def tortoise_ctx():
    """Initialise Tortoise with SQLite in-memory for each test function."""
    async with TortoiseContext() as ctx:
        await ctx.init(
            db_url="sqlite://:memory:",
            modules={"models": _PLAN_MODELS},
            _enable_global_fallback=True,
        )
        await ctx.generate_schemas(safe=True)
        yield ctx


@pytest.mark.anyio
@_SKIP_TORTOISE
class TestCreatePlan:
    async def test_create_plan(self, tortoise_ctx):
        from db.managers.plan_manager import PlanManager

        mgr = PlanManager()
        plan = await mgr.create_plan("Recon Phase", description="Initial recon", scope="red-team")

        assert plan.id is not None
        assert plan.title == "Recon Phase"
        assert plan.description == "Initial recon"
        assert plan.scope == "red-team"
        assert plan.status == "draft"


@pytest.mark.anyio
@_SKIP_TORTOISE
class TestAddTaskAndReady:
    async def test_add_task_and_ready(self, tortoise_ctx):
        from db.managers.plan_manager import PlanManager

        mgr = PlanManager()
        plan = await mgr.create_plan("Exploit Phase")
        t1 = await mgr.add_task(plan.id, "Port Scan", sequence=1)
        t2 = await mgr.add_task(plan.id, "Vuln Scan", sequence=2)

        ready = await mgr.get_ready_tasks(plan.id)
        ready_ids = {t.id for t in ready}

        assert t1.id in ready_ids
        assert t2.id in ready_ids
        assert len(ready) == 2

    async def test_plan_summary_counts(self, tortoise_ctx):
        from db.managers.plan_manager import PlanManager

        mgr = PlanManager()
        plan = await mgr.create_plan("Summary Test")
        await mgr.add_task(plan.id, "T1")
        t2 = await mgr.add_task(plan.id, "T2")
        await mgr.set_task_status(t2.id, "done")

        summary = await mgr.get_plan_summary(plan.id)
        assert summary["id"] == plan.id
        assert summary["tasks"]["pending"] == 1
        assert summary["tasks"]["done"] == 1


@pytest.mark.anyio
@_SKIP_TORTOISE
class TestTaskDependency:
    async def test_task_not_ready_while_dep_pending(self, tortoise_ctx):
        from db.managers.plan_manager import PlanManager

        mgr = PlanManager()
        plan = await mgr.create_plan("Dep Test")
        dep_task = await mgr.add_task(plan.id, "Must run first")
        blocked_task = await mgr.add_task(plan.id, "Waits for dep")

        await mgr.add_dependency(blocked_task.id, dep_task.id)

        ready = await mgr.get_ready_tasks(plan.id)
        ready_ids = {t.id for t in ready}

        # dep_task has no deps → ready; blocked_task dep is still pending → not ready
        assert dep_task.id in ready_ids
        assert blocked_task.id not in ready_ids

    async def test_task_becomes_ready_after_dep_done(self, tortoise_ctx):
        from db.managers.plan_manager import PlanManager

        mgr = PlanManager()
        plan = await mgr.create_plan("Dep Done Test")
        dep_task = await mgr.add_task(plan.id, "Step 1")
        blocked_task = await mgr.add_task(plan.id, "Step 2")
        await mgr.add_dependency(blocked_task.id, dep_task.id)

        await mgr.set_task_status(dep_task.id, "done")

        ready = await mgr.get_ready_tasks(plan.id)
        ready_ids = {t.id for t in ready}

        assert blocked_task.id in ready_ids
        assert dep_task.id not in ready_ids  # already done, not pending


@pytest.mark.anyio
@_SKIP_TORTOISE
class TestTodoManagement:
    async def test_add_todo_to_task(self, tortoise_ctx):
        from db.managers.plan_manager import PlanManager

        mgr = PlanManager()
        plan = await mgr.create_plan("Todo Test")
        task = await mgr.add_task(plan.id, "Implementation")
        todo1 = await mgr.add_todo(task.id, "Write core logic", assignee="alice")
        todo2 = await mgr.add_todo(task.id, "Add tests", assignee="bob")

        assert todo1.id is not None
        assert todo1.content == "Write core logic"
        assert todo1.assignee == "alice"
        assert todo2.content == "Add tests"
        assert todo2.assignee == "bob"

    async def test_plan_hierarchy_with_todos(self, tortoise_ctx):
        from db.managers.plan_manager import PlanManager

        mgr = PlanManager()
        plan = await mgr.create_plan("Hierarchy Test")
        t1 = await mgr.add_task(plan.id, "Task 1", sequence=1)
        t2 = await mgr.add_task(plan.id, "Task 2", sequence=2)
        todo1 = await mgr.add_todo(t1.id, "Todo 1.1")
        todo2 = await mgr.add_todo(t1.id, "Todo 1.2")
        todo3 = await mgr.add_todo(t2.id, "Todo 2.1")

        hierarchy = await mgr.get_plan_hierarchy(plan.id)
        assert len(hierarchy["tasks"]) == 2
        assert len(hierarchy["tasks"][0]["todos"]) == 2
        assert len(hierarchy["tasks"][1]["todos"]) == 1

    async def test_plan_summary_with_todos(self, tortoise_ctx):
        from db.managers.plan_manager import PlanManager

        mgr = PlanManager()
        plan = await mgr.create_plan("Summary with Todos")
        task = await mgr.add_task(plan.id, "Task 1")
        todo1 = await mgr.add_todo(task.id, "Todo 1")
        todo2 = await mgr.add_todo(task.id, "Todo 2")
        await mgr.set_todo_status(todo1.id, "done")

        summary = await mgr.get_plan_summary(plan.id)
        assert summary["todos"]["pending"] == 1
        assert summary["todos"]["done"] == 1
