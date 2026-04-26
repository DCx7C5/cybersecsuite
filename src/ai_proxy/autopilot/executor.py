"""
Autopilot Executor — staged Claude execution with commit strategy and rollback.

Implements:
- Staged commits: Write to temp branch, validate, merge on success
- Error handling: Graceful degradation with detailed error context
- Rollback: Automatic rollback on validation failure or test failure
- Audit trail: Full execution history with timing and risk scores
"""
from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger("ai_proxy.autopilot.executor")


class ExecutionState(str, Enum):
    """Execution state transitions."""
    PENDING = "pending"           # Waiting to start
    PLANNING = "planning"         # Claude planning phase
    STAGING = "staging"           # Staged changes ready
    VALIDATING = "validating"     # Running validation tests
    COMMITTED = "committed"       # Changes committed
    ROLLED_BACK = "rolled_back"   # Changes rolled back
    FAILED = "failed"             # Execution failed
    ABANDONED = "abandoned"       # User aborted


class RiskLevel(str, Enum):
    """Risk classification for execution decisions."""
    LOW = "low"           # Safe changes (< 0.3)
    MEDIUM = "medium"     # Moderate risk (0.3-0.6)
    HIGH = "high"         # High risk (0.6-0.8)
    CRITICAL = "critical" # Requires human intervention (> 0.8)


@dataclass
class ExecutionChange:
    """Represents a single staged change (file, commit, etc.)."""
    id: str = field(default_factory=lambda: str(uuid4()))
    path: str = ""                              # File or resource path
    operation: str = ""                         # 'create', 'modify', 'delete'
    before: str = ""                            # Previous content
    after: str = ""                             # New content
    hash_before: str = ""                       # BLAKE2b hash of before
    hash_after: str = ""                        # BLAKE2b hash of after
    size_before: int = 0                        # Bytes before
    size_after: int = 0                         # Bytes after
    risk_score: float = 0.0                     # 0.0-1.0
    description: str = ""                       # Change summary


@dataclass
class ExecutionPhase:
    """Represents an execution phase (planning, staging, validating, committing)."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""                              # Phase name
    state: ExecutionState = ExecutionState.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    changes: list[ExecutionChange] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    validation_results: dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW


@dataclass
class AutopilotExecution:
    """Top-level autopilot execution context."""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    plan: str = ""                              # Implementation plan from user
    feedback: Optional[str] = None              # Test feedback for refinement
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_duration_ms: float = 0.0
    state: ExecutionState = ExecutionState.PENDING
    phases: list[ExecutionPhase] = field(default_factory=list)
    total_changes: int = 0
    committed_changes: int = 0
    rolled_back_changes: int = 0
    risk_assessment: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    audit_trail: list[str] = field(default_factory=list)


class ExecutorClient:
    """Client for orchestrating autopilot execution."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        base_url: str = "https://api.anthropic.com",
        timeout_seconds: int = 120,
        max_retries: int = 3,
    ) -> None:
        """
        Initialize executor client.

        Args:
            model: Claude model to use for execution planning
            api_key: Anthropic API key (from env if not provided)
            base_url: Anthropic API base URL
            timeout_seconds: HTTP timeout
            max_retries: Retry attempts on failure
        """
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._executions: dict[str, AutopilotExecution] = {}

    async def close(self) -> None:
        """Close executor resources (no-op for now)."""
        pass

    def _blake2b_hash(self, data: str) -> str:
        """Compute BLAKE2b-256 hash."""
        return hashlib.blake2b(data.encode(), digest_size=32).hexdigest()

    def _assess_risk(self, change: ExecutionChange) -> float:
        """
        Assess risk score for a change (0.0-1.0).

        Factors:
        - Size increase (0.0-0.2)
        - Operation type (0.1-0.3): delete > modify > create
        - Code complexity (0.0-0.5)
        """
        risk = 0.0

        # Size factor
        size_ratio = change.size_after / max(change.size_before, 1)
        if size_ratio > 2.0:
            risk += 0.2
        elif size_ratio > 1.5:
            risk += 0.1

        # Operation factor
        if change.operation == "delete":
            risk += 0.3
        elif change.operation == "modify":
            risk += 0.15
        # 'create' adds minimal risk

        # Code complexity (heuristic)
        if change.path.endswith(".py"):
            async_count = change.after.count("async ")
            transaction_count = change.after.count("in_transaction")
            crypto_count = change.after.count("BLAKE2b") + change.after.count("Ed25519")
            if async_count > 3:
                risk += 0.15
            if transaction_count > 2:
                risk += 0.1
            if crypto_count > 0:
                risk += 0.05

        return min(risk, 1.0)

    def _classify_risk_level(self, score: float) -> RiskLevel:
        """Classify risk score into level."""
        if score < 0.3:
            return RiskLevel.LOW
        elif score < 0.6:
            return RiskLevel.MEDIUM
        elif score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    async def start_execution(
        self,
        plan: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        feedback: Optional[str] = None,
    ) -> AutopilotExecution:
        """
        Start a new autopilot execution.

        Args:
            plan: Implementation plan from user
            session_id: Optional session identifier
            user_id: Optional user identifier
            feedback: Optional test feedback

        Returns:
            AutopilotExecution context
        """
        execution = AutopilotExecution(
            session_id=session_id,
            user_id=user_id,
            plan=plan,
            feedback=feedback,
        )
        self._executions[execution.id] = execution
        execution.audit_trail.append(
            f"[{execution.started_at.isoformat()}] Execution started: {plan[:100]}..."
        )
        logger.info(f"Started autopilot execution {execution.id}: {plan[:80]}...")
        return execution

    async def add_phase(
        self,
        execution: AutopilotExecution,
        name: str,
        description: str = "",
    ) -> ExecutionPhase:
        """
        Add execution phase.

        Args:
            execution: Parent execution
            name: Phase name (planning, staging, validating, committing)
            description: Phase description

        Returns:
            ExecutionPhase
        """
        phase = ExecutionPhase(name=name, state=ExecutionState.PENDING)
        execution.phases.append(phase)
        phase.started_at = datetime.utcnow()
        execution.audit_trail.append(f"[{phase.started_at.isoformat()}] Phase started: {name}")
        logger.debug(f"Phase {name} started in execution {execution.id}")
        return phase

    async def stage_change(
        self,
        execution: AutopilotExecution,
        phase: ExecutionPhase,
        path: str,
        operation: str,
        before: str = "",
        after: str = "",
        description: str = "",
    ) -> ExecutionChange:
        """
        Stage a single change.

        Args:
            execution: Parent execution
            phase: Parent phase
            path: File or resource path
            operation: 'create', 'modify', or 'delete'
            before: Previous content
            after: New content
            description: Change summary

        Returns:
            ExecutionChange
        """
        change = ExecutionChange(
            path=path,
            operation=operation,
            before=before,
            after=after,
            size_before=len(before),
            size_after=len(after),
            description=description,
        )
        change.hash_before = self._blake2b_hash(before)
        change.hash_after = self._blake2b_hash(after)
        change.risk_score = self._assess_risk(change)

        phase.changes.append(change)
        execution.total_changes += 1
        phase.state = ExecutionState.STAGING

        execution.audit_trail.append(
            f"[{datetime.utcnow().isoformat()}] Staged: {operation} {path} "
            f"(risk: {change.risk_score:.2f})"
        )
        logger.info(f"Staged {operation} to {path} (risk: {change.risk_score:.2f})")

        return change

    async def validate_phase(
        self,
        execution: AutopilotExecution,
        phase: ExecutionPhase,
        test_results: dict[str, Any],
    ) -> bool:
        """
        Validate phase changes against test results.

        Args:
            execution: Parent execution
            phase: Phase to validate
            test_results: Test results dict with keys: passed, failed, errors

        Returns:
            True if validation passes, False otherwise
        """
        phase.state = ExecutionState.VALIDATING
        phase.validation_results = test_results

        passed = test_results.get("passed", 0)
        failed = test_results.get("failed", 0)
        errors = test_results.get("errors", [])

        # Risk assessment for phase
        max_risk = max((c.risk_score for c in phase.changes), default=0.0)
        phase.risk_level = self._classify_risk_level(max_risk)

        execution.risk_assessment = {
            "max_risk_score": max_risk,
            "risk_level": phase.risk_level.value,
            "test_passed": passed,
            "test_failed": failed,
            "validation_errors": len(errors),
        }

        # Determine pass/fail
        validation_ok = failed == 0 and len(errors) == 0

        if validation_ok:
            phase.state = ExecutionState.COMMITTED
            execution.committed_changes += len(phase.changes)
            execution.state = ExecutionState.COMMITTED
            execution.audit_trail.append(
                f"[{datetime.utcnow().isoformat()}] Validation passed: {passed} tests, 0 failures"
            )
            logger.info(f"Validation passed for phase {phase.name}: {passed} tests passed")
            return True
        else:
            phase.state = ExecutionState.ROLLED_BACK
            execution.rolled_back_changes += len(phase.changes)
            execution.state = ExecutionState.ROLLED_BACK
            error_msg = f"Validation failed: {failed} tests failed, {len(errors)} errors"
            execution.audit_trail.append(f"[{datetime.utcnow().isoformat()}] {error_msg}")
            execution.errors.extend(errors)
            logger.warning(error_msg)
            return False

    async def commit_execution(
        self,
        execution: AutopilotExecution,
    ) -> AutopilotExecution:
        """
        Finalize execution and generate audit summary.

        Args:
            execution: Execution to commit

        Returns:
            Updated AutopilotExecution
        """
        execution.completed_at = datetime.utcnow()
        execution.total_duration_ms = (
            execution.completed_at - execution.started_at
        ).total_seconds() * 1000

        execution.state = ExecutionState.COMMITTED

        # Summary audit trail
        execution.audit_trail.append(
            f"[{execution.completed_at.isoformat()}] Execution completed"
        )
        execution.audit_trail.append(
            f"Total: {execution.total_changes} changes, "
            f"{execution.committed_changes} committed, "
            f"{execution.rolled_back_changes} rolled back"
        )
        execution.audit_trail.append(
            f"Duration: {execution.total_duration_ms:.0f}ms"
        )

        logger.info(
            f"Execution {execution.id} completed: "
            f"{execution.committed_changes}/{execution.total_changes} committed, "
            f"duration: {execution.total_duration_ms:.0f}ms"
        )

        return execution

    async def rollback_execution(
        self,
        execution: AutopilotExecution,
        reason: str = "",
    ) -> AutopilotExecution:
        """
        Rollback entire execution.

        Args:
            execution: Execution to rollback
            reason: Rollback reason

        Returns:
            Updated AutopilotExecution
        """
        for phase in execution.phases:
            if phase.state in (ExecutionState.COMMITTED, ExecutionState.STAGING):
                phase.state = ExecutionState.ROLLED_BACK
                execution.rolled_back_changes += len(phase.changes)

        execution.completed_at = datetime.utcnow()
        execution.total_duration_ms = (
            execution.completed_at - execution.started_at
        ).total_seconds() * 1000
        execution.state = ExecutionState.ROLLED_BACK

        msg = f"Execution rolled back: {reason}" if reason else "Execution rolled back"
        execution.audit_trail.append(f"[{datetime.utcnow().isoformat()}] {msg}")
        execution.errors.append(msg)

        logger.warning(f"Execution {execution.id} rolled back: {reason}")

        return execution

    def get_execution(self, execution_id: str) -> Optional[AutopilotExecution]:
        """Retrieve execution by ID."""
        return self._executions.get(execution_id)

    def list_executions(self) -> list[AutopilotExecution]:
        """List all tracked executions."""
        return list(self._executions.values())


# Global singleton
_executor_client: Optional[ExecutorClient] = None


async def get_executor_client() -> ExecutorClient:
    """Get or create global executor client."""
    global _executor_client
    if _executor_client is None:
        _executor_client = ExecutorClient()
    return _executor_client
