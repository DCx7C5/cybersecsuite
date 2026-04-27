"""
Worker State Machine Models — t366, t367, t368.

Implements:
- t366: Worker state machine with transitions (queued → running → paused → complete/failed)
- t367: Session state save/restore with integrity verification (BLAKE2b hashing)
- t368: Worker-scope integration with audit trail and permission checks

Features:
- State transitions with timestamp and reason tracking
- Query/filter by state
- Execution history and bookmark persistence
- Scope-based filtering and permission enforcement
- Integrity verification via BLAKE2b hashing
- Audit trail per scope
"""
from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any

from tortoise import fields, models


class WorkerState(str, Enum):
    """Worker state machine transitions."""
    QUEUED = "queued"          # Task waiting to be picked up
    RUNNING = "running"        # Task actively executing
    PAUSED = "paused"          # Task paused (checkpoint/manual)
    COMPLETED = "completed"    # Task completed successfully
    FAILED = "failed"          # Task failed with error


class WorkerStateTransition(models.Model):
    """
    Track worker state transitions with timestamp, reason, and context.
    
    Implements t366: Worker state machine with full audit trail.
    """
    id = fields.IntField(primary_key=True)
    
    # Worker identification
    worker_id = fields.CharField(
        max_length=128,
        db_index=True,
        description="Unique worker identifier"
    )
    worker_type = fields.CharField(
        max_length=64,
        default="generic",
        description="Type of worker (e.g., forensic_processor, threat_enricher)"
    )
    
    # Scope binding (t368)
    project = fields.ForeignKeyField(
        "models.Project",
        related_name="worker_transitions",
        on_delete=fields.CASCADE,
        db_index=True,
        description="Project scope"
    )
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="worker_transitions",
        on_delete=fields.CASCADE,
        null=True,
        db_index=True,
        description="Session scope (optional, for session-level workers)"
    )
    
    # State tracking
    from_state = fields.CharEnumField(
        WorkerState,
        null=True,
        description="Previous worker state"
    )
    to_state = fields.CharEnumField(
        WorkerState,
        db_index=True,
        description="New worker state"
    )
    
    # Transition metadata
    reason = fields.CharField(
        max_length=256,
        default="",
        description="Reason for state transition (e.g., 'manual pause', 'checkpoint triggered')"
    )
    metadata = fields.JSONField(
        default=dict,
        description="Additional context: error_message, checkpoint_reason, etc."
    )
    
    # Timestamps
    transitioned_at = fields.DatetimeField(
        auto_now_add=True,
        description="When state transition occurred"
    )
    created_at = fields.DatetimeField(
        auto_now_add=True,
        description="Record creation timestamp"
    )
    updated_at = fields.DatetimeField(
        auto_now=True,
        description="Record last update timestamp"
    )
    
    class Meta:
        table = "worker_state_transitions"
        indexes = [
            ("worker_id", "transitioned_at"),
            ("project_id", "to_state"),
            ("session_id", "to_state"),
            ("to_state",),  # For filtering by state
        ]
        ordering = ["-transitioned_at"]
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"WorkerStateTransition("
            f"worker_id={self.worker_id}, "
            f"{self.from_state} → {self.to_state}, "
            f"reason={self.reason}"
            f")"
        )


class WorkerSession(models.Model):
    """
    Worker session context and execution state.
    
    Implements t367: Save/restore worker context, execution history, bookmarks.
    """
    id = fields.IntField(primary_key=True)
    
    # Worker and session identification
    worker_id = fields.CharField(
        max_length=128,
        db_index=True,
        unique=True,
        description="Unique worker identifier (one session per worker)"
    )
    worker_type = fields.CharField(
        max_length=64,
        default="generic",
        description="Type of worker"
    )
    name = fields.CharField(
        max_length=256,
        default="",
        description="Human-readable worker name"
    )
    description = fields.TextField(
        default="",
        description="Worker description"
    )
    
    # Scope binding (t368)
    project = fields.ForeignKeyField(
        "models.Project",
        related_name="worker_sessions",
        on_delete=fields.CASCADE,
        db_index=True,
        description="Project scope"
    )
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="worker_sessions",
        on_delete=fields.CASCADE,
        null=True,
        db_index=True,
        description="Session scope (optional)"
    )
    
    # Current state
    current_state = fields.CharEnumField(
        WorkerState,
        default=WorkerState.QUEUED,
        db_index=True,
        description="Current worker state"
    )
    
    # Execution context (t367 - save/restore)
    context_data = fields.JSONField(
        default=dict,
        description="Worker context: variables, state, configuration"
    )
    
    # Execution history
    execution_history = fields.JSONField(
        default=list,
        description="List of execution steps: {timestamp, action, status, result}"
    )
    
    # Bookmarks (t367 - save/restore)
    bookmarks = fields.JSONField(
        default=dict,
        description="Execution bookmarks: {key: {line, position, state, timestamp}}"
    )
    
    # Integrity verification (t367)
    context_hash = fields.CharField(
        max_length=64,
        default="",
        description="BLAKE2b-256 hash of serialized context_data for integrity"
    )
    execution_history_hash = fields.CharField(
        max_length=64,
        default="",
        description="BLAKE2b-256 hash of execution_history for integrity"
    )
    bookmarks_hash = fields.CharField(
        max_length=64,
        default="",
        description="BLAKE2b-256 hash of bookmarks for integrity"
    )
    
    # Metrics
    start_time = fields.DatetimeField(
        auto_now_add=True,
        description="Worker session start time"
    )
    last_activity_at = fields.DatetimeField(
        auto_now=True,
        description="Last activity timestamp"
    )
    total_duration_ms = fields.BigIntField(
        default=0,
        description="Total execution time in milliseconds"
    )
    steps_executed = fields.IntField(
        default=0,
        description="Total execution steps completed"
    )
    
    # Audit trail
    created_at = fields.DatetimeField(
        auto_now_add=True,
        description="Record creation timestamp"
    )
    updated_at = fields.DatetimeField(
        auto_now=True,
        description="Record last update timestamp"
    )
    
    class Meta:
        table = "worker_sessions"
        indexes = [
            ("project_id", "current_state"),
            ("session_id", "current_state"),
            ("worker_id",),
            ("current_state",),
        ]
        ordering = ["-last_activity_at"]
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"WorkerSession("
            f"worker_id={self.worker_id}, "
            f"state={self.current_state}, "
            f"steps={self.steps_executed}"
            f")"
        )
    
    @staticmethod
    def _compute_hash(data: Any) -> str:
        """
        Compute BLAKE2b-256 hash of data for integrity verification (t367).
        
        Args:
            data: Any JSON-serializable data
            
        Returns:
            64-character hex hash
        """
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.blake2b(serialized.encode(), digest_size=32).hexdigest()
    
    def update_context(self, context_data: dict[str, Any]) -> None:
        """
        Update worker context with integrity verification.
        
        Args:
            context_data: New context data
        """
        self.context_data = context_data
        self.context_hash = self._compute_hash(context_data)
    
    def update_execution_history(self, history: list[dict[str, Any]]) -> None:
        """
        Update execution history with integrity verification.
        
        Args:
            history: List of execution step records
        """
        self.execution_history = history
        self.execution_history_hash = self._compute_hash(history)
    
    def update_bookmarks(self, bookmarks: dict[str, Any]) -> None:
        """
        Update bookmarks with integrity verification.
        
        Args:
            bookmarks: Dictionary of bookmark records
        """
        self.bookmarks = bookmarks
        self.bookmarks_hash = self._compute_hash(bookmarks)
    
    async def verify_integrity(self) -> tuple[bool, list[str]]:
        """
        Verify integrity of saved context, history, and bookmarks (t367).
        
        Returns:
            (is_valid, list of integrity failures)
        """
        failures: list[str] = []
        
        # Verify context
        computed_context_hash = self._compute_hash(self.context_data)
        if computed_context_hash != self.context_hash:
            failures.append(
                f"Context integrity check failed: "
                f"expected {self.context_hash}, got {computed_context_hash}"
            )
        
        # Verify execution history
        computed_history_hash = self._compute_hash(self.execution_history)
        if computed_history_hash != self.execution_history_hash:
            failures.append(
                f"Execution history integrity check failed: "
                f"expected {self.execution_history_hash}, got {computed_history_hash}"
            )
        
        # Verify bookmarks
        computed_bookmarks_hash = self._compute_hash(self.bookmarks)
        if computed_bookmarks_hash != self.bookmarks_hash:
            failures.append(
                f"Bookmarks integrity check failed: "
                f"expected {self.bookmarks_hash}, got {computed_bookmarks_hash}"
            )
        
        return (len(failures) == 0, failures)


class WorkerAuditLog(models.Model):
    """
    Audit trail for worker operations per scope (t368).
    
    Tracks all worker state changes, scope transitions, and permission checks
    for accountability and forensic analysis.
    """
    id = fields.IntField(primary_key=True)
    
    # Worker identification
    worker_id = fields.CharField(
        max_length=128,
        db_index=True,
        description="Unique worker identifier"
    )
    
    # Scope (t368)
    project = fields.ForeignKeyField(
        "models.Project",
        related_name="worker_audit_logs",
        on_delete=fields.CASCADE,
        db_index=True,
        description="Project scope"
    )
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="worker_audit_logs",
        on_delete=fields.CASCADE,
        null=True,
        db_index=True,
        description="Session scope (optional)"
    )
    scope_level = fields.CharField(
        max_length=16,
        choices=[
            ("global", "global"),
            ("app", "app"),
            ("project", "project"),
            ("runtime", "runtime"),
            ("session", "session"),
        ],
        default="session",
        db_index=True,
        description="Scope level where action occurred"
    )
    
    # Action details
    action = fields.CharField(
        max_length=64,
        db_index=True,
        description="Action performed: state_transition, checkpoint, pause, resume, etc."
    )
    status = fields.CharField(
        max_length=32,
        choices=[
            ("success", "success"),
            ("failure", "failure"),
            ("denied", "denied"),
        ],
        default="success",
        description="Action result status"
    )
    
    # Permission check (t368)
    permission_check_passed = fields.BooleanField(
        default=True,
        db_index=True,
        description="Whether permission check passed for this action"
    )
    permission_required = fields.CharField(
        max_length=128,
        default="",
        description="Permission that was checked (e.g., 'worker_state_transition')"
    )
    
    # Audit details
    details = fields.JSONField(
        default=dict,
        description="Additional audit details: from_state, to_state, reason, error, etc."
    )
    
    # Timestamps
    occurred_at = fields.DatetimeField(
        auto_now_add=True,
        description="When action occurred"
    )
    created_at = fields.DatetimeField(
        auto_now_add=True,
        description="Record creation timestamp"
    )
    
    class Meta:
        table = "worker_audit_logs"
        indexes = [
            ("worker_id", "occurred_at"),
            ("project_id", "scope_level"),
            ("session_id", "scope_level"),
            ("action", "status"),
            ("permission_check_passed",),
        ]
        ordering = ["-occurred_at"]
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"WorkerAuditLog("
            f"worker_id={self.worker_id}, "
            f"action={self.action}, "
            f"status={self.status}, "
            f"scope={self.scope_level}"
            f")"
        )
