"""Tests for PlanManager: CRUD, ready-task logic, dependency gating, and todo management."""
from __future__ import annotations

import sys
from datetime import datetime, timedelta

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


@pytest.mark.anyio
@_SKIP_TORTOISE
class TestTaskClaiming:
    async def test_claim_task_success(self, tortoise_ctx):
        """Test successful atomic task claiming."""
        from db.managers.plan_manager import PlanManager

        mgr = PlanManager()
        plan = await mgr.create_plan("Claim Test")
        task = await mgr.add_task(plan.id, "Claimable Task")

        claimed = await mgr.claim_task(task.id, claimed_by="agent_1")

        assert claimed is True
        refreshed = await mgr.get_ready_tasks(plan.id)
        assert len(refreshed) == 0  # Task is now in_progress, not pending

        updated_task = await Task.get(id=task.id)
        assert updated_task.claimed_by == "agent_1"
        assert updated_task.status == "in_progress"
        assert updated_task.claimed_at is not None

    async def test_claim_task_already_claimed(self, tortoise_ctx):
        """Test that claiming an already-claimed task fails."""
        from db.managers.plan_manager import PlanManager
        from db.models.plan import Task

        mgr = PlanManager()
        plan = await mgr.create_plan("Claim Test 2")
        task = await mgr.add_task(plan.id, "Already Claimed Task")

        claimed1 = await mgr.claim_task(task.id, claimed_by="agent_1")
        assert claimed1 is True

        claimed2 = await mgr.claim_task(task.id, claimed_by="agent_2")
        assert claimed2 is False

        updated_task = await Task.get(id=task.id)
        assert updated_task.claimed_by == "agent_1"  # Still agent_1, not agent_2

    async def test_concurrent_claim_race(self, tortoise_ctx):
        """Simulate race condition: both agents try to claim same task."""
        from db.managers.plan_manager import PlanManager
        from db.models.plan import Task
        import asyncio

        mgr = PlanManager()
        plan = await mgr.create_plan("Race Test")
        task = await mgr.add_task(plan.id, "Race Task")

        async def attempt_claim(agent_name: str) -> bool:
            return await mgr.claim_task(task.id, claimed_by=agent_name)

        result1, result2 = await asyncio.gather(
            attempt_claim("agent_a"),
            attempt_claim("agent_b"),
        )

        assert result1 or result2  # One must succeed
        assert not (result1 and result2)  # But not both

        updated_task = await Task.get(id=task.id)
        assert updated_task.claimed_by in ("agent_a", "agent_b")
        assert updated_task.status == "in_progress"

    async def test_get_ready_tasks_excludes_claimed(self, tortoise_ctx):
        """Test that get_ready_tasks filters out claimed tasks."""
        from db.managers.plan_manager import PlanManager

        mgr = PlanManager()
        plan = await mgr.create_plan("Filter Test")
        t1 = await mgr.add_task(plan.id, "Task 1")
        t2 = await mgr.add_task(plan.id, "Task 2")

        await mgr.claim_task(t1.id, claimed_by="agent_1")

        ready = await mgr.get_ready_tasks(plan.id)
        ready_ids = {t.id for t in ready}

        assert t1.id not in ready_ids  # Claimed task not in ready list
        assert t2.id in ready_ids  # Unclaimed pending task is ready

    async def test_claim_task_with_lease_expiry(self, tortoise_ctx):
        """Test claiming with lease expiry time."""
        from db.managers.plan_manager import PlanManager
        from db.models.plan import Task

        mgr = PlanManager()
        plan = await mgr.create_plan("Lease Test")
        task = await mgr.add_task(plan.id, "Lease Task")

        future_time = datetime.now() + timedelta(minutes=30)
        claimed = await mgr.claim_task(task.id, claimed_by="agent_lease", lease_expires_at=future_time)

        assert claimed is True
        updated_task = await Task.get(id=task.id)
        assert updated_task.lease_expires_at == future_time

    async def test_lease_expiry_cleanup(self, tortoise_ctx):
        """Test cleanup_expired_leases resets orphaned tasks."""
        from db.managers.plan_manager import PlanManager
        from db.models.plan import Task

        mgr = PlanManager()
        plan = await mgr.create_plan("Cleanup Test")
        t1 = await mgr.add_task(plan.id, "Expired Task")
        t2 = await mgr.add_task(plan.id, "Valid Task")

        past_time = datetime.now() - timedelta(minutes=10)
        future_time = datetime.now() + timedelta(minutes=10)

        await mgr.claim_task(t1.id, claimed_by="agent_expired", lease_expires_at=past_time)
        await mgr.claim_task(t2.id, claimed_by="agent_valid", lease_expires_at=future_time)

        cleaned_count = await mgr.cleanup_expired_leases()

        assert cleaned_count == 1

        updated_t1 = await Task.get(id=t1.id)
        assert updated_t1.claimed_by == ""
        assert updated_t1.status == "pending"
        assert updated_t1.lease_expires_at is None

        updated_t2 = await Task.get(id=t2.id)
        assert updated_t2.claimed_by == "agent_valid"
        assert updated_t2.status == "in_progress"

    async def test_set_task_status_clears_claim_on_done(self, tortoise_ctx):
        """Test that set_task_status clears claim when transitioning to done."""
        from db.managers.plan_manager import PlanManager
        from db.models.plan import Task

        mgr = PlanManager()
        plan = await mgr.create_plan("Done Test")
        task = await mgr.add_task(plan.id, "Complete Task")

        await mgr.claim_task(task.id, claimed_by="agent_complete")

        updated_task = await mgr.set_task_status(task.id, "done")

        assert updated_task.status == "done"
        assert updated_task.claimed_by == ""
        assert updated_task.claimed_at is None
        assert updated_task.lease_expires_at is None

    async def test_set_task_status_clears_claim_on_blocked(self, tortoise_ctx):
        """Test that set_task_status clears claim when transitioning to blocked."""
        from db.managers.plan_manager import PlanManager
        from db.models.plan import Task

        mgr = PlanManager()
        plan = await mgr.create_plan("Blocked Test")
        task = await mgr.add_task(plan.id, "Blocked Task")

        await mgr.claim_task(task.id, claimed_by="agent_blocked")

        updated_task = await mgr.set_task_status(task.id, "blocked")

        assert updated_task.status == "blocked"
        assert updated_task.claimed_by == ""
        assert updated_task.claimed_at is None
        assert updated_task.lease_expires_at is None

