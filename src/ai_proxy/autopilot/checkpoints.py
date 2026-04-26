"""
Autopilot Checkpoints — human-in-the-loop pause points and budget enforcement.

Implements:
- Checkpoint states: PAUSE, RESUME, ABORT, MODIFY
- Risk-based pausing: Risk score > 0.7
- Test failure detection: Pause after 3 consecutive failures
- Budget enforcement: Pause when token limit reached
- Task classification: Pause on unknown/unclassified tasks
- Event logging: Full audit trail with metadata
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger("ai_proxy.autopilot.checkpoints")


class CheckpointState(str, Enum):
    """Checkpoint interaction states."""
    PAUSE = "pause"           # Awaiting human decision
    RESUME = "resume"         # Continue execution
    ABORT = "abort"           # Stop execution
    MODIFY = "modify"         # Proceed with modifications


class CheckpointReason(str, Enum):
    """Reasons for checkpoint triggers."""
    HIGH_RISK = "high_risk"                     # Risk score > 0.7
    TEST_FAILURES = "test_failures"             # 3+ consecutive test failures
    BUDGET_DEPLETED = "budget_depleted"         # Token limit reached
    UNKNOWN_TASK = "unknown_task"               # Unclassified task
    COST_THRESHOLD = "cost_threshold"           # Cost threshold exceeded
    MANUAL_PAUSE = "manual_pause"               # User requested pause


@dataclass
class CheckpointEvent:
    """Single checkpoint event with metadata."""
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    reason: CheckpointReason = CheckpointReason.MANUAL_PAUSE
    state_before: str = ""                      # State before checkpoint
    state_after: str = ""                       # State after checkpoint
    risk_score: float = 0.0                     # Current risk assessment
    test_failure_count: int = 0                 # Consecutive test failures
    tokens_used: int = 0                        # Tokens consumed
    cost_usd: float = 0.0                       # Cost in USD
    budget_remaining: Optional[float] = None    # Remaining budget
    metadata: dict[str, Any] = field(default_factory=dict)
    description: str = ""                       # Event description


@dataclass
class BudgetTracker:
    """Track token and cost budgets per session/user."""
    session_id: str = ""
    user_id: Optional[str] = None
    max_tokens: int = 1_000_000                 # Default 1M tokens
    max_cost_usd: float = 100.0                 # Default $100
    tokens_used: int = 0
    cost_usd: float = 0.0
    requests_count: int = 0
    last_request_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def tokens_remaining(self) -> int:
        """Calculate remaining tokens."""
        return max(0, self.max_tokens - self.tokens_used)

    @property
    def cost_remaining(self) -> float:
        """Calculate remaining budget."""
        return max(0.0, self.max_cost_usd - self.cost_usd)

    @property
    def token_percentage(self) -> float:
        """Percentage of token budget used."""
        return (self.tokens_used / self.max_tokens) * 100

    @property
    def cost_percentage(self) -> float:
        """Percentage of cost budget used."""
        return (self.cost_usd / self.max_cost_usd) * 100

    def is_budget_depleted(self) -> bool:
        """Check if budget is exhausted."""
        return self.tokens_remaining <= 0 or self.cost_remaining <= 0.0


@dataclass
class TaskClassification:
    """Task classification and complexity assessment."""
    task_id: str = ""
    task_type: str = ""                         # 'file_create', 'api_endpoint', 'test', etc.
    is_classified: bool = False                 # True if classification confidence > 0.8
    confidence: float = 0.0                     # Classification confidence (0.0-1.0)
    complexity: str = ""                        # 'simple', 'moderate', 'complex'
    requires_human_review: bool = False         # True if confidence < 0.5
    metadata: dict[str, Any] = field(default_factory=dict)


class CheckpointManager:
    """Manage checkpoint triggers and human-in-the-loop workflow."""

    def __init__(self) -> None:
        """Initialize checkpoint manager."""
        self._checkpoints: dict[str, CheckpointEvent] = {}
        self._budgets: dict[str, BudgetTracker] = {}
        self._test_failure_streak: dict[str, int] = {}  # session -> count
        self._paused_executions: set[str] = set()  # Paused execution IDs
        self._task_classifications: dict[str, TaskClassification] = {}

    async def create_budget(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        max_tokens: int = 1_000_000,
        max_cost_usd: float = 100.0,
    ) -> BudgetTracker:
        """
        Create or retrieve budget tracker.

        Args:
            session_id: Session identifier
            user_id: Optional user identifier
            max_tokens: Maximum tokens allowed
            max_cost_usd: Maximum cost in USD

        Returns:
            BudgetTracker
        """
        if session_id in self._budgets:
            return self._budgets[session_id]

        budget = BudgetTracker(
            session_id=session_id,
            user_id=user_id,
            max_tokens=max_tokens,
            max_cost_usd=max_cost_usd,
        )
        self._budgets[session_id] = budget
        logger.info(
            f"Created budget for {session_id}: {max_tokens} tokens, ${max_cost_usd}"
        )
        return budget

    async def get_budget(self, session_id: str) -> Optional[BudgetTracker]:
        """Retrieve budget tracker."""
        return self._budgets.get(session_id)

    async def track_usage(
        self,
        session_id: str,
        tokens: int,
        cost_usd: float,
    ) -> BudgetTracker:
        """
        Track token and cost usage.

        Args:
            session_id: Session identifier
            tokens: Tokens consumed
            cost_usd: Cost in USD

        Returns:
            Updated BudgetTracker
        """
        budget = self._budgets.get(session_id)
        if not budget:
            budget = await self.create_budget(session_id)

        budget.tokens_used += tokens
        budget.cost_usd += cost_usd
        budget.requests_count += 1
        budget.last_request_at = datetime.utcnow()

        logger.debug(
            f"Usage tracked for {session_id}: +{tokens} tokens, +${cost_usd:.4f} "
            f"(total: {budget.tokens_used}/{budget.max_tokens} tokens, "
            f"${budget.cost_usd:.2f}/${budget.max_cost_usd})"
        )

        return budget

    async def check_high_risk(
        self,
        execution_id: str,
        session_id: str,
        risk_score: float,
        threshold: float = 0.7,
    ) -> Optional[CheckpointEvent]:
        """
        Check and trigger HIGH_RISK checkpoint.

        Args:
            execution_id: Execution identifier
            session_id: Session identifier
            risk_score: Current risk score (0.0-1.0)
            threshold: Risk threshold for pause (default 0.7)

        Returns:
            CheckpointEvent if triggered, None otherwise
        """
        if risk_score > threshold:
            checkpoint = await self._trigger_checkpoint(
                execution_id=execution_id,
                session_id=session_id,
                reason=CheckpointReason.HIGH_RISK,
                risk_score=risk_score,
                description=f"Risk score {risk_score:.2f} exceeds threshold {threshold}",
            )
            return checkpoint
        return None

    async def check_test_failures(
        self,
        execution_id: str,
        session_id: str,
        failed: bool,
        failure_threshold: int = 3,
    ) -> Optional[CheckpointEvent]:
        """
        Track test failures and trigger checkpoint on streak.

        Args:
            execution_id: Execution identifier
            session_id: Session identifier
            failed: True if test failed
            failure_threshold: Threshold for pause (default 3)

        Returns:
            CheckpointEvent if triggered, None otherwise
        """
        key = session_id
        current_streak = self._test_failure_streak.get(key, 0)

        if failed:
            current_streak += 1
            self._test_failure_streak[key] = current_streak
            logger.debug(f"Test failure streak for {session_id}: {current_streak}")

            if current_streak >= failure_threshold:
                checkpoint = await self._trigger_checkpoint(
                    execution_id=execution_id,
                    session_id=session_id,
                    reason=CheckpointReason.TEST_FAILURES,
                    test_failure_count=current_streak,
                    description=f"{current_streak} consecutive test failures",
                )
                return checkpoint
        else:
            # Reset streak on success
            self._test_failure_streak[key] = 0

        return None

    async def check_budget(
        self,
        execution_id: str,
        session_id: str,
    ) -> Optional[CheckpointEvent]:
        """
        Check budget depletion and trigger checkpoint if needed.

        Args:
            execution_id: Execution identifier
            session_id: Session identifier

        Returns:
            CheckpointEvent if budget depleted, None otherwise
        """
        budget = self._budgets.get(session_id)
        if not budget:
            return None

        if budget.is_budget_depleted():
            checkpoint = await self._trigger_checkpoint(
                execution_id=execution_id,
                session_id=session_id,
                reason=CheckpointReason.BUDGET_DEPLETED,
                tokens_used=budget.tokens_used,
                cost_usd=budget.cost_usd,
                description=f"Budget depleted: {budget.tokens_used}/{budget.max_tokens} tokens, "
                f"${budget.cost_usd:.2f}/${budget.max_cost_usd}",
            )
            return checkpoint

        # Warn at 90% threshold
        if budget.token_percentage > 90 or budget.cost_percentage > 90:
            logger.warning(
                f"Budget warning for {session_id}: "
                f"{budget.token_percentage:.0f}% tokens, {budget.cost_percentage:.0f}% cost"
            )

        return None

    async def check_cost_threshold(
        self,
        execution_id: str,
        session_id: str,
        threshold_percentage: float = 0.8,
    ) -> Optional[CheckpointEvent]:
        """
        Check if cost threshold is exceeded.

        Args:
            execution_id: Execution identifier
            session_id: Session identifier
            threshold_percentage: Cost threshold as percentage (default 0.8 = 80%)

        Returns:
            CheckpointEvent if threshold exceeded, None otherwise
        """
        budget = self._budgets.get(session_id)
        if not budget:
            return None

        if budget.cost_percentage >= (threshold_percentage * 100):
            checkpoint = await self._trigger_checkpoint(
                execution_id=execution_id,
                session_id=session_id,
                reason=CheckpointReason.COST_THRESHOLD,
                cost_usd=budget.cost_usd,
                budget_remaining=budget.cost_remaining,
                description=f"Cost threshold reached: {budget.cost_percentage:.0f}% of budget used",
            )
            return checkpoint

        return None

    async def check_task_classification(
        self,
        execution_id: str,
        session_id: str,
        task_id: str,
        task_type: str,
        confidence: float,
    ) -> Optional[CheckpointEvent]:
        """
        Check task classification and trigger checkpoint if unclassified.

        Args:
            execution_id: Execution identifier
            session_id: Session identifier
            task_id: Task identifier
            task_type: Task type
            confidence: Classification confidence (0.0-1.0)

        Returns:
            CheckpointEvent if unclassified, None otherwise
        """
        classification = TaskClassification(
            task_id=task_id,
            task_type=task_type,
            is_classified=confidence > 0.8,
            confidence=confidence,
            requires_human_review=confidence < 0.5,
        )
        self._task_classifications[task_id] = classification

        if confidence < 0.5:
            checkpoint = await self._trigger_checkpoint(
                execution_id=execution_id,
                session_id=session_id,
                reason=CheckpointReason.UNKNOWN_TASK,
                metadata={
                    "task_id": task_id,
                    "task_type": task_type,
                    "confidence": confidence,
                },
                description=f"Unknown task '{task_type}' (confidence: {confidence:.2f})",
            )
            return checkpoint

        return None

    async def _trigger_checkpoint(
        self,
        execution_id: str,
        session_id: str,
        reason: CheckpointReason,
        risk_score: float = 0.0,
        test_failure_count: int = 0,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        budget_remaining: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
        description: str = "",
    ) -> CheckpointEvent:
        """
        Internal: Trigger a checkpoint event.

        Returns:
            CheckpointEvent
        """
        checkpoint = CheckpointEvent(
            reason=reason,
            state_before="running",
            state_after="paused",
            risk_score=risk_score,
            test_failure_count=test_failure_count,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            budget_remaining=budget_remaining,
            metadata=metadata or {},
            description=description,
        )
        self._checkpoints[checkpoint.id] = checkpoint
        self._paused_executions.add(execution_id)

        logger.warning(
            f"Checkpoint triggered for {execution_id} ({session_id}): "
            f"{reason.value} - {description}"
        )

        return checkpoint

    async def resolve_checkpoint(
        self,
        checkpoint_id: str,
        state: CheckpointState,
        modifications: Optional[dict[str, Any]] = None,
    ) -> CheckpointEvent:
        """
        Resolve checkpoint with human decision.

        Args:
            checkpoint_id: Checkpoint ID
            state: Human decision (RESUME, ABORT, MODIFY)
            modifications: Optional modifications for MODIFY state

        Returns:
            Updated CheckpointEvent
        """
        checkpoint = self._checkpoints.get(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")

        checkpoint.state_after = state.value
        checkpoint.metadata["resolved_at"] = datetime.utcnow().isoformat()
        checkpoint.metadata["modifications"] = modifications or {}

        logger.info(
            f"Checkpoint {checkpoint_id} resolved: {state.value} "
            f"(reason: {checkpoint.reason.value})"
        )

        return checkpoint

    async def resume_execution(self, execution_id: str) -> bool:
        """Mark execution as resumed."""
        if execution_id in self._paused_executions:
            self._paused_executions.discard(execution_id)
            logger.info(f"Execution {execution_id} resumed")
            return True
        return False

    async def abort_execution(self, execution_id: str, reason: str = "") -> bool:
        """Mark execution as aborted."""
        if execution_id in self._paused_executions:
            self._paused_executions.discard(execution_id)
            logger.warning(f"Execution {execution_id} aborted: {reason}")
            return True
        return False

    def is_paused(self, execution_id: str) -> bool:
        """Check if execution is paused."""
        return execution_id in self._paused_executions

    def get_checkpoint(self, checkpoint_id: str) -> Optional[CheckpointEvent]:
        """Retrieve checkpoint event."""
        return self._checkpoints.get(checkpoint_id)

    def list_checkpoints(
        self,
        session_id: Optional[str] = None,
        reason: Optional[CheckpointReason] = None,
    ) -> list[CheckpointEvent]:
        """
        List checkpoint events with optional filtering.

        Args:
            session_id: Filter by session (not stored in event, would need execution context)
            reason: Filter by reason

        Returns:
            List of CheckpointEvent
        """
        events = list(self._checkpoints.values())
        if reason:
            events = [e for e in events if e.reason == reason]
        return sorted(events, key=lambda e: e.timestamp, reverse=True)

    def get_budget_summary(self, session_id: str) -> dict[str, Any]:
        """Get budget summary."""
        budget = self._budgets.get(session_id)
        if not budget:
            return {}
        return {
            "session_id": budget.session_id,
            "tokens_used": budget.tokens_used,
            "tokens_remaining": budget.tokens_remaining,
            "tokens_percentage": budget.token_percentage,
            "cost_usd": budget.cost_usd,
            "cost_remaining": budget.cost_remaining,
            "cost_percentage": budget.cost_percentage,
            "requests_count": budget.requests_count,
            "is_depleted": budget.is_budget_depleted(),
        }


# Global singleton
_checkpoint_manager: Optional[CheckpointManager] = None


async def get_checkpoint_manager() -> CheckpointManager:
    """Get or create global checkpoint manager."""
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager
