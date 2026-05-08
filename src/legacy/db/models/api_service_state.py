"""
ApiService State — Session-scoped tracking of active API service health and usage.

Tracks the current active AI API service per session, including health status,
response times, error counts, and token usage. This model enables intelligent
service fallback decisions and session-aware load balancing.

Session lifecycle:
- Created when a new session starts (first AI API service call)
- Updated after each service interaction (health check, response time record)
- Queried for fallback decisions when service becomes unavailable
- Cleaned up when session ends or times out
"""
from tortoise import fields
from css.core.db.models.base import BaseModel
from css.core.db.fields import CostField


class ApiServiceState(BaseModel):
    """
    Session-scoped AI API service state tracking.

    Tracks:
    - Current active API service for this session
    - Health status (ok, degraded, error)
    - Performance metrics (last response time, error count)
    - Usage metrics (calls this session, tokens this session)
    """

    id = fields.BigIntField(primary_key=True)

    # Session and API service references
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="api_service_states",
        on_delete=fields.CASCADE,
        db_index=True,
        description="Session this API service state belongs to"
    )
    api_service = fields.ForeignKeyField(
        "models.ApiService",
        related_name="session_states",
        on_delete=fields.CASCADE,
        db_index=True,
        description="Active API service for this session"
    )

    # Health status
    health_status = fields.CharField(
        max_length=16,
        choices=[("ok", "ok"), ("degraded", "degraded"), ("error", "error")],
        default="ok",
        db_index=True,
        description="Health status: ok, degraded, or error"
    )
    is_active = fields.BooleanField(
        default=True,
        db_index=True,
        description="Is this provider currently active for the session?"
    )

    # Performance metrics
    last_response_time_ms = fields.IntField(
        default=0,
        description="Last response time in milliseconds"
    )
    avg_response_time_ms = fields.IntField(
        default=0,
        description="Average response time in milliseconds for this session"
    )
    max_response_time_ms = fields.IntField(
        default=0,
        description="Maximum response time in milliseconds for this session"
    )

    # Error tracking
    error_count = fields.IntField(
        default=0,
        db_index=True,
        description="Number of errors encountered this session"
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

    # Usage metrics
    total_calls = fields.IntField(
        default=0,
        description="Total API calls to this provider this session"
    )
    total_input_tokens = fields.BigIntField(
        default=0,
        description="Total input tokens used this session"
    )
    total_output_tokens = fields.BigIntField(
        default=0,
        description="Total output tokens used this session"
    )
    total_cost_usd = CostField(
        max_digits=14,
        decimal_places=8,
        default=0,
        description="Total cost in USD for this session"
    )

    # Metadata and audit
    first_used_at = fields.DatetimeField(
        auto_now_add=True,
        description="When this API service was first used in this session"
    )
    last_used_at = fields.DatetimeField(
        auto_now=True,
        description="When this API service was last used"
    )
    created_at = fields.DatetimeField(
        auto_now_add=True,
        description="Record creation timestamp"
    )
    updated_at = fields.DatetimeField(
        auto_now=True,
        description="Record last update timestamp"
    )

    # Metadata for flexibility
    metadata = fields.JSONField(
        default=dict,
        description="Additional API service state metadata"
    )

    class Meta:
        table = "api_service_states"
        table_description_plural = "API Service States"
        table_description_singular = "API Service State"
        # Composite index for session + api_service lookups
        indexes = [
            ("session_id", "api_service_id"),
            ("session_id", "is_active"),
            ("session_id", "health_status"),
            ("session_id", "error_count"),
        ]
        # Ensure one active API service per session (upsert pattern)
        unique_together = (("session_id", "api_service_id"),)
        ordering = ["-last_used_at"]

    def __str__(self) -> str:
        """String representation of API service state."""
        return (
            f"ApiServiceState("
            f"session={self.session_id}, "
            f"api_service={self.api_service_id}, "
            f"status={self.health_status}"
            f")"
        )
