"""
AI Provider State — Session-scoped tracking of active provider health and usage.

Tracks the current active AI provider per session, including health status,
response times, error counts, and token usage. This model enables intelligent
provider fallback decisions and session-aware load balancing.

Session lifecycle:
- Created when a new session starts (first AI provider call)
- Updated after each provider interaction (health check, response time record)
- Queried for fallback decisions when provider becomes unavailable
- Cleaned up when session ends or times out
"""
from tortoise import fields
from tortoise.models import Model


class AIProviderState(Model):
    """
    Session-scoped AI provider state tracking.

    Tracks:
    - Current active provider for this session
    - Health status (ok, degraded, error)
    - Performance metrics (last response time, error count)
    - Usage metrics (calls this session, tokens this session)
    """

    id = fields.IntField(primary_key=True)

    # Session and provider references
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="ai_provider_states",
        on_delete=fields.CASCADE,
        db_index=True,
        description="Session this provider state belongs to"
    )
    provider = fields.ForeignKeyField(
        "models.Provider",
        related_name="session_states",
        on_delete=fields.CASCADE,
        db_index=True,
        description="Active provider for this session"
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
    total_cost_usd = fields.DecimalField(
        max_digits=14,
        decimal_places=8,
        default=0,
        description="Total cost in USD for this session"
    )

    # Metadata and audit
    first_used_at = fields.DatetimeField(
        auto_now_add=True,
        description="When this provider was first used in this session"
    )
    last_used_at = fields.DatetimeField(
        auto_now=True,
        description="When this provider was last used"
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
        description="Additional provider state metadata"
    )

    class Meta:
        table = "ai_provider_states"
        # Composite index for session + provider lookups
        indexes = [
            ("session_id", "provider_id"),
            ("session_id", "is_active"),
            ("session_id", "health_status"),
            ("session_id", "error_count"),
        ]
        # Ensure one active provider per session (upsert pattern)
        unique_together = (("session_id", "provider_id"),)
        ordering = ["-last_used_at"]

    def __str__(self) -> str:
        """String representation of provider state."""
        return (
            f"AIProviderState("
            f"session={self.session_id}, "
            f"provider={self.provider_id}, "
            f"status={self.health_status}"
            f")"
        )
