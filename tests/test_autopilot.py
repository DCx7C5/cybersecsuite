"""
Test Suite — autopilot executor, checkpoints, and cost estimator.

Tests:
- ExecutorClient: execution phases, changes, validation, rollback
- CheckpointManager: risk triggers, budget tracking, test failures
- CostEstimator: token estimation, cost calculation, Redis tracking
"""
from __future__ import annotations

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Import components
from ai_proxy.autopilot.executor import (
    AutopilotExecution,
    ExecutionChange,
    ExecutionPhase,
    ExecutionState,
    RiskLevel,
    ExecutorClient,
)
from ai_proxy.autopilot.checkpoints import (
    BudgetTracker,
    CheckpointEvent,
    CheckpointManager,
    CheckpointReason,
    CheckpointState,
    TaskClassification,
)
from ai_proxy.autopilot.cost_estimator import (
    CostEstimate,
    CostEstimator,
    CostResult,
)


# ════════════════════════════════════════════════════════════════════════════════
# EXECUTOR TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestExecutorClient:
    """Test ExecutorClient."""

    @pytest.fixture
    def executor(self) -> ExecutorClient:
        """Create executor client."""
        return ExecutorClient(
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
        )

    @pytest.mark.asyncio
    async def test_start_execution(self, executor: ExecutorClient) -> None:
        """Test starting execution."""
        execution = await executor.start_execution(
            plan="Implement autopilot feature",
            session_id="session-1",
            user_id="user-1",
        )

        assert execution.plan == "Implement autopilot feature"
        assert execution.session_id == "session-1"
        assert execution.user_id == "user-1"
        assert execution.state == ExecutionState.PENDING
        assert len(execution.audit_trail) > 0

    @pytest.mark.asyncio
    async def test_add_phase(self, executor: ExecutorClient) -> None:
        """Test adding execution phase."""
        execution = await executor.start_execution(plan="Test plan")
        phase = await executor.add_phase(execution, name="planning")

        assert phase.name == "planning"
        assert phase.state == ExecutionState.PENDING
        assert len(execution.phases) == 1

    @pytest.mark.asyncio
    async def test_stage_change(self, executor: ExecutorClient) -> None:
        """Test staging a change."""
        execution = await executor.start_execution(plan="Test plan")
        phase = await executor.add_phase(execution, name="staging")

        change = await executor.stage_change(
            execution=execution,
            phase=phase,
            path="src/test.py",
            operation="create",
            before="",
            after="print('hello')",
            description="Create test file",
        )

        assert change.path == "src/test.py"
        assert change.operation == "create"
        assert change.size_after > 0
        assert change.risk_score >= 0.0
        assert len(phase.changes) == 1
        assert execution.total_changes == 1

    def test_risk_assessment(self, executor: ExecutorClient) -> None:
        """Test risk assessment for changes."""
        # Low risk: small create
        change1 = ExecutionChange(
            path="test.txt",
            operation="create",
            before="",
            after="hello",
            size_after=5,
        )
        risk1 = executor._assess_risk(change1)
        assert risk1 < 0.3

        # High risk: large delete
        change2 = ExecutionChange(
            path="main.py",
            operation="delete",
            before="x" * 10000,
            after="",
            size_before=10000,
        )
        risk2 = executor._assess_risk(change2)
        assert risk2 >= 0.3

    def test_risk_classification(self, executor: ExecutorClient) -> None:
        """Test risk level classification."""
        assert executor._classify_risk_level(0.2) == RiskLevel.LOW
        assert executor._classify_risk_level(0.4) == RiskLevel.MEDIUM
        assert executor._classify_risk_level(0.7) == RiskLevel.HIGH
        assert executor._classify_risk_level(0.9) == RiskLevel.CRITICAL

    @pytest.mark.asyncio
    async def test_validate_phase_success(self, executor: ExecutorClient) -> None:
        """Test successful phase validation."""
        execution = await executor.start_execution(plan="Test plan")
        phase = await executor.add_phase(execution, name="validating")

        await executor.stage_change(
            execution, phase, "test.py", "create", "", "code",
        )

        test_results = {"passed": 5, "failed": 0, "errors": []}
        result = await executor.validate_phase(execution, phase, test_results)

        assert result is True
        assert phase.state == ExecutionState.COMMITTED
        assert execution.state == ExecutionState.COMMITTED

    @pytest.mark.asyncio
    async def test_validate_phase_failure(self, executor: ExecutorClient) -> None:
        """Test failed phase validation."""
        execution = await executor.start_execution(plan="Test plan")
        phase = await executor.add_phase(execution, name="validating")

        await executor.stage_change(
            execution, phase, "test.py", "create", "", "code",
        )

        test_results = {"passed": 2, "failed": 3, "errors": ["Test 1 failed"]}
        result = await executor.validate_phase(execution, phase, test_results)

        assert result is False
        assert phase.state == ExecutionState.ROLLED_BACK
        assert execution.state == ExecutionState.ROLLED_BACK

    @pytest.mark.asyncio
    async def test_commit_execution(self, executor: ExecutorClient) -> None:
        """Test committing execution."""
        execution = await executor.start_execution(plan="Test plan")
        execution = await executor.commit_execution(execution)

        assert execution.state == ExecutionState.COMMITTED
        assert execution.completed_at is not None
        assert execution.total_duration_ms > 0

    @pytest.mark.asyncio
    async def test_rollback_execution(self, executor: ExecutorClient) -> None:
        """Test rolling back execution."""
        execution = await executor.start_execution(plan="Test plan")
        phase = await executor.add_phase(execution, name="staging")

        await executor.stage_change(
            execution, phase, "test.py", "create", "", "code",
        )

        execution = await executor.rollback_execution(
            execution,
            reason="User requested rollback",
        )

        assert execution.state == ExecutionState.ROLLED_BACK
        assert execution.rolled_back_changes > 0


# ════════════════════════════════════════════════════════════════════════════════
# CHECKPOINT TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestCheckpointManager:
    """Test CheckpointManager."""

    @pytest.fixture
    def manager(self) -> CheckpointManager:
        """Create checkpoint manager."""
        return CheckpointManager()

    @pytest.mark.asyncio
    async def test_create_budget(self, manager: CheckpointManager) -> None:
        """Test creating budget tracker."""
        budget = await manager.create_budget(
            session_id="session-1",
            user_id="user-1",
            max_tokens=100_000,
            max_cost_usd=50.0,
        )

        assert budget.session_id == "session-1"
        assert budget.user_id == "user-1"
        assert budget.max_tokens == 100_000
        assert budget.max_cost_usd == 50.0
        assert budget.tokens_remaining == 100_000

    @pytest.mark.asyncio
    async def test_track_usage(self, manager: CheckpointManager) -> None:
        """Test tracking usage."""
        await manager.create_budget("session-1", max_tokens=100_000)
        budget = await manager.track_usage("session-1", tokens=5_000, cost_usd=0.15)

        assert budget.tokens_used == 5_000
        assert budget.cost_usd == 0.15
        assert budget.requests_count == 1

    @pytest.mark.asyncio
    async def test_budget_depletion(self, manager: CheckpointManager) -> None:
        """Test budget depletion detection."""
        await manager.create_budget("session-1", max_tokens=1_000, max_cost_usd=1.0)
        budget = await manager.track_usage("session-1", tokens=950, cost_usd=0.95)

        assert not budget.is_budget_depleted()
        assert budget.token_percentage > 90

        await manager.track_usage("session-1", tokens=100, cost_usd=0.1)
        budget = await manager.get_budget("session-1")
        assert budget.is_budget_depleted()

    @pytest.mark.asyncio
    async def test_check_high_risk(self, manager: CheckpointManager) -> None:
        """Test high risk checkpoint trigger."""
        checkpoint = await manager.check_high_risk(
            execution_id="exec-1",
            session_id="session-1",
            risk_score=0.75,
            threshold=0.7,
        )

        assert checkpoint is not None
        assert checkpoint.reason == CheckpointReason.HIGH_RISK
        assert checkpoint.risk_score == 0.75
        assert manager.is_paused("exec-1")

    @pytest.mark.asyncio
    async def test_check_test_failures(self, manager: CheckpointManager) -> None:
        """Test test failure checkpoint trigger."""
        # First two failures don't trigger
        cp1 = await manager.check_test_failures("exec-1", "session-1", failed=True)
        assert cp1 is None

        cp2 = await manager.check_test_failures("exec-1", "session-1", failed=True)
        assert cp2 is None

        # Third failure triggers checkpoint
        cp3 = await manager.check_test_failures("exec-1", "session-1", failed=True)
        assert cp3 is not None
        assert cp3.reason == CheckpointReason.TEST_FAILURES
        assert cp3.test_failure_count == 3

    @pytest.mark.asyncio
    async def test_check_budget_checkpoint(self, manager: CheckpointManager) -> None:
        """Test budget depletion checkpoint."""
        await manager.create_budget("session-1", max_tokens=1_000)
        await manager.track_usage("session-1", tokens=1_000, cost_usd=0.0)

        checkpoint = await manager.check_budget("exec-1", "session-1")

        assert checkpoint is not None
        assert checkpoint.reason == CheckpointReason.BUDGET_DEPLETED

    @pytest.mark.asyncio
    async def test_check_task_classification(self, manager: CheckpointManager) -> None:
        """Test task classification checkpoint."""
        # Low confidence triggers
        checkpoint = await manager.check_task_classification(
            execution_id="exec-1",
            session_id="session-1",
            task_id="task-1",
            task_type="unknown_operation",
            confidence=0.3,
        )

        assert checkpoint is not None
        assert checkpoint.reason == CheckpointReason.UNKNOWN_TASK

        # High confidence doesn't trigger
        checkpoint2 = await manager.check_task_classification(
            execution_id="exec-2",
            session_id="session-1",
            task_id="task-2",
            task_type="file_create",
            confidence=0.95,
        )

        assert checkpoint2 is None

    @pytest.mark.asyncio
    async def test_resolve_checkpoint(self, manager: CheckpointManager) -> None:
        """Test resolving checkpoint."""
        checkpoint = await manager.check_high_risk("exec-1", "session-1", 0.75)

        resolved = await manager.resolve_checkpoint(
            checkpoint_id=checkpoint.id,
            state=CheckpointState.RESUME,
            modifications={"skip_tests": True},
        )

        assert resolved.state_after == "resume"
        assert "modifications" in resolved.metadata

    @pytest.mark.asyncio
    async def test_resume_execution(self, manager: CheckpointManager) -> None:
        """Test resuming execution."""
        await manager.check_high_risk("exec-1", "session-1", 0.75)
        assert manager.is_paused("exec-1")

        resumed = await manager.resume_execution("exec-1")
        assert resumed is True
        assert not manager.is_paused("exec-1")

    @pytest.mark.asyncio
    async def test_get_budget_summary(self, manager: CheckpointManager) -> None:
        """Test budget summary."""
        await manager.create_budget("session-1", max_tokens=100_000, max_cost_usd=50.0)
        await manager.track_usage("session-1", tokens=10_000, cost_usd=5.0)

        summary = manager.get_budget_summary("session-1")

        assert summary["tokens_used"] == 10_000
        assert summary["cost_usd"] == 5.0
        assert summary["requests_count"] == 1
        assert not summary["is_depleted"]


# ════════════════════════════════════════════════════════════════════════════════
# COST ESTIMATOR TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestCostEstimator:
    """Test CostEstimator."""

    @pytest.fixture
    def estimator(self) -> CostEstimator:
        """Create cost estimator."""
        return CostEstimator(enable_redis_tracking=False)

    @pytest.mark.asyncio
    async def test_estimate_cost(self, estimator: CostEstimator) -> None:
        """Test cost estimation."""
        estimate = await estimator.estimate_cost(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": "Hello, world!"}],
        )

        assert estimate.model == "claude-3-5-sonnet-20241022"
        assert estimate.estimated_input_tokens > 0
        assert estimate.total_cost_usd > 0

    @pytest.mark.asyncio
    async def test_model_cost_lookup(self, estimator: CostEstimator) -> None:
        """Test model cost lookup."""
        cost1 = estimator._get_model_cost("claude-3-5-sonnet-20241022")
        assert cost1["input"] == 3.0
        assert cost1["output"] == 15.0

        cost2 = estimator._get_model_cost("qwen-turbo")
        assert cost2["input"] == 0.2
        assert cost2["output"] == 0.6

    @pytest.mark.asyncio
    async def test_record_cost(self, estimator: CostEstimator) -> None:
        """Test recording cost."""
        result = await estimator.record_cost(
            request_id="req-1",
            model="claude-3-5-sonnet-20241022",
            session_id="session-1",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1500.0,
        )

        assert result.total_tokens == 150
        assert result.total_cost_usd > 0
        assert "X-Tier-Cost" in result.headers
        assert "X-Tier-Speed" in result.headers
        assert "1500" in result.headers["X-Tier-Speed"]

    @pytest.mark.asyncio
    async def test_cost_comparison(self, estimator: CostEstimator) -> None:
        """Test cost comparison across models."""
        messages = [{"role": "user", "content": "Write 1000 words about AI"}]

        cost_haiku = await estimator.estimate_cost("claude-3-haiku-20240307", messages)
        cost_sonnet = await estimator.estimate_cost("claude-3-5-sonnet-20241022", messages)
        cost_opus = await estimator.estimate_cost("claude-3-opus-20240229", messages)

        # Verify cost ordering
        assert cost_haiku.total_cost_usd < cost_sonnet.total_cost_usd
        assert cost_sonnet.total_cost_usd < cost_opus.total_cost_usd


# ════════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """Integration tests across components."""

    @pytest.fixture
    def executor(self) -> ExecutorClient:
        return ExecutorClient()

    @pytest.fixture
    def manager(self) -> CheckpointManager:
        return CheckpointManager()

    @pytest.fixture
    def estimator(self) -> CostEstimator:
        return CostEstimator(enable_redis_tracking=False)

    @pytest.mark.asyncio
    async def test_execution_with_checkpoints(
        self,
        executor: ExecutorClient,
        manager: CheckpointManager,
    ) -> None:
        """Test execution with checkpoint integration."""
        # Start execution
        execution = await executor.start_execution(
            plan="Test feature",
            session_id="session-1",
            user_id="user-1",
        )

        # Create budget
        await manager.create_budget(
            session_id="session-1",
            max_tokens=100_000,
            max_cost_usd=50.0,
        )

        # Plan phase
        plan_phase = await executor.add_phase(execution, "planning")

        # Stage changes
        await executor.stage_change(
            execution, plan_phase, "src/feature.py", "create", "", "code",
        )

        # Check for high risk
        checkpoint = await manager.check_high_risk("exec-1", "session-1", 0.4)
        assert checkpoint is None  # Low risk, no checkpoint

        # Validate
        await executor.validate_phase(
            execution,
            plan_phase,
            {"passed": 10, "failed": 0, "errors": []},
        )

        # Finalize
        execution = await executor.commit_execution(execution)
        assert execution.state == ExecutionState.COMMITTED

    @pytest.mark.asyncio
    async def test_execution_with_cost_tracking(
        self,
        executor: ExecutorClient,
        estimator: CostEstimator,
        manager: CheckpointManager,
    ) -> None:
        """Test execution with cost estimation and tracking."""
        # Estimate cost
        estimate = await estimator.estimate_cost(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": "Test"}],
        )

        # Track usage
        await manager.create_budget("session-1", max_cost_usd=10.0)
        budget = await manager.track_usage(
            "session-1",
            tokens=estimate.total_estimated_tokens,
            cost_usd=estimate.total_cost_usd,
        )

        # Check cost threshold
        checkpoint = await manager.check_cost_threshold(
            "exec-1",
            "session-1",
            threshold_percentage=0.9,
        )

        assert budget.cost_usd <= budget.max_cost_usd


# ════════════════════════════════════════════════════════════════════════════════
# FIXTURES & MARKERS
# ════════════════════════════════════════════════════════════════════════════════

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
def anyio_backend():
    """Specify asyncio backend."""
    return "asyncio"
