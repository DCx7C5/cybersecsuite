"""
Worker Context — Session-scoped background worker state tracking.

Tracks the state and context of background workers processing tasks for a session:
- Active task count and task IDs
- Queue depth and pending work
- Error count and recent errors
- Context awareness (recently accessed files/functions)
- Auto-cleanup with TTL for stale entries

Enables:
- Session-aware worker load balancing
- Task deduplication
- Context-aware task execution
- Stale worker cleanup
"""
from datetime import datetime, timedelta
from tortoise import fields
from tortoise.models import Model


class WorkerContext(Model):
    """
    Session-scoped background worker state and context tracking.

    Tracks:
    - Active task count and IDs
    - Queue depth
    - Error state and recent errors
    - Context (recently accessed files/functions for cache locality)
    - TTL for auto-cleanup of stale entries
    """

    id = fields.IntField(primary_key=True)

    # Session reference
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="worker_contexts",
        on_delete=fields.CASCADE,
        db_index=True,
        description="Session this worker context belongs to"
    )

    # Worker identification
    worker_id = fields.CharField(
        max_length=128,
        db_index=True,
        description="Unique identifier for this worker"
    )
    worker_type = fields.CharField(
        max_length=64,
        default="generic",
        description="Type of worker (e.g., 'forensic_processor', 'threat_intel_enricher')"
    )

    # Task state
    active_task_count = fields.IntField(
        default=0,
        description="Number of currently active tasks"
    )
    active_task_ids = fields.JSONField(
        default=list,
        description="List of active task IDs being processed by this worker"
    )

    # Queue state
    queue_depth = fields.IntField(
        default=0,
        description="Number of pending tasks in worker queue"
    )
    pending_task_ids = fields.JSONField(
        default=list,
        description="List of pending task IDs waiting to be processed"
    )

    # Performance tracking
    total_tasks_processed = fields.BigIntField(
        default=0,
        description="Total tasks processed by this worker since session start"
    )
    total_processing_time_ms = fields.BigIntField(
        default=0,
        description="Total processing time in milliseconds"
    )
    avg_task_duration_ms = fields.IntField(
        default=0,
        description="Average task duration in milliseconds"
    )
    max_task_duration_ms = fields.IntField(
        default=0,
        description="Maximum task duration in milliseconds"
    )

    # Error tracking
    error_count = fields.IntField(
        default=0,
        db_index=True,
        description="Number of errors encountered by this worker"
    )
    consecutive_errors = fields.IntField(
        default=0,
        description="Consecutive error count (reset on success)"
    )
    last_error = fields.CharField(
        max_length=512,
        default="",
        description="Last error message"
    )
    last_error_at = fields.DatetimeField(
        null=True,
        description="Timestamp of last error"
    )
    recent_errors = fields.JSONField(
        default=list,
        description="List of recent errors with timestamps and messages"
    )

    # Context awareness
    recently_accessed_files = fields.JSONField(
        default=list,
        description="Files recently accessed by this worker (for cache locality)"
    )
    recently_accessed_functions = fields.JSONField(
        default=list,
        description="Functions/operations recently executed (for context optimization)"
    )
    context_metadata = fields.JSONField(
        default=dict,
        description="Additional context metadata for intelligent task routing"
    )

    # Health and activity
    is_active = fields.BooleanField(
        default=True,
        db_index=True,
        description="Is this worker currently active?"
    )
    health_status = fields.CharField(
        max_length=16,
        choices=[("healthy", "healthy"), ("degraded", "degraded"), ("unhealthy", "unhealthy")],
        default="healthy",
        description="Worker health status"
    )

    # Lifecycle and TTL
    first_seen_at = fields.DatetimeField(
        auto_now_add=True,
        description="When this worker was first seen"
    )
    last_heartbeat_at = fields.DatetimeField(
        auto_now=True,
        description="Last heartbeat timestamp"
    )
    created_at = fields.DatetimeField(
        auto_now_add=True,
        description="Record creation timestamp"
    )
    updated_at = fields.DatetimeField(
        auto_now=True,
        description="Record last update timestamp"
    )
    expires_at = fields.DatetimeField(
        null=True,
        db_index=True,
        description="Record expiration timestamp (auto-cleanup TTL)"
    )

    # Metadata
    metadata = fields.JSONField(
        default=dict,
        description="Additional worker metadata"
    )

    class Meta:
        table = "worker_contexts"
        # Composite indexes for common queries
        indexes = [
            ("session", "worker_id"),
            ("session", "is_active"),
            ("session", "health_status"),
            ("expires_at",),  # For cleanup queries
            ("last_heartbeat_at",),  # For stale worker detection
        ]
        # Ensure one context per worker per session
        unique_together = (("session", "worker_id"),)
        ordering = ["-last_heartbeat_at"]

    def __str__(self) -> str:
        """String representation of worker context."""
        return (
            f"WorkerContext("
            f"session={self.session_id}, "
            f"worker_id={self.worker_id}, "
            f"active_tasks={self.active_task_count}, "
            f"queue_depth={self.queue_depth}"
            f")"
        )

    async def is_stale(self, stale_threshold_seconds: int = 3600) -> bool:
        """
        Check if this worker context is stale (no heartbeat for threshold time).

        Args:
            stale_threshold_seconds: Seconds of inactivity before marking stale

        Returns:
            True if worker hasn't sent heartbeat within threshold
        """
        if not self.last_heartbeat_at:
            return False
        time_since_heartbeat = datetime.utcnow() - self.last_heartbeat_at
        return time_since_heartbeat > timedelta(seconds=stale_threshold_seconds)

    def set_expiration(self, ttl_hours: int = 24) -> None:
        """
        Set record expiration timestamp for auto-cleanup.

        Args:
            ttl_hours: Time-to-live in hours from now
        """
        self.expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
