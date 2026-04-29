"""
ApiService Events — Immutable audit trail of API service state changes per session.

Captures all API service-related events in chronological order:
- SERVICE_CHANGED: Active API service switched
- FALLBACK_TRIGGERED: Fallback to alternative service due to failure
- ERROR_RECORDED: Error occurred with current service
- HEALTH_CHECK: Health status update
- RATE_LIMIT: Rate limit hit
- TIMEOUT: Request timeout

This is an append-only event log (no updates) that enables full audit trail
and service history analysis per session.
"""
from tortoise import fields
from tortoise.models import Model


class ApiServiceEvent(Model):
    """
    Immutable audit trail of API service events per session.

    Each row represents a single service-related event in chronological order.
    Events are never updated or deleted (append-only log).

    Event types:
    - SERVICE_CHANGED: Active API service switched
    - FALLBACK_TRIGGERED: Switched to fallback service
    - ERROR_RECORDED: Error occurred
    - HEALTH_CHECK: Health status check
    - RATE_LIMIT: Rate limit encountered
    - TIMEOUT: Request timeout
    - SUCCESS: Successful request
    """

    id = fields.BigIntField(primary_key=True)

    # Session and API service references
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="api_service_events",
        on_delete=fields.CASCADE,
        db_index=True,
        description="Session this event belongs to"
    )

    # Event details
    event_type = fields.CharField(
        max_length=32,
        choices=[
            ("SERVICE_CHANGED", "SERVICE_CHANGED"),
            ("FALLBACK_TRIGGERED", "FALLBACK_TRIGGERED"),
            ("ERROR_RECORDED", "ERROR_RECORDED"),
            ("HEALTH_CHECK", "HEALTH_CHECK"),
            ("RATE_LIMIT", "RATE_LIMIT"),
            ("TIMEOUT", "TIMEOUT"),
            ("SUCCESS", "SUCCESS"),
        ],
        db_index=True,
        description="Type of event"
    )

    # API service references
    old_api_service = fields.ForeignKeyField(
        "models.ApiService",
        related_name="events_old",
        on_delete=fields.SET_NULL,
        null=True,
        description="Previous API service (for SERVICE_CHANGED and FALLBACK_TRIGGERED)"
    )
    new_api_service = fields.ForeignKeyField(
        "models.ApiService",
        related_name="events_new",
        on_delete=fields.SET_NULL,
        null=True,
        description="New API service (for SERVICE_CHANGED and FALLBACK_TRIGGERED)"
    )

    # Event context
    reason = fields.CharField(
        max_length=256,
        default="",
        description="Reason for the event (e.g., 'health_check_failed', 'rate_limit_exceeded')"
    )
    error_message = fields.TextField(
        default="",
        description="Error message if event_type is ERROR_RECORDED"
    )

    # Performance context
    response_time_ms = fields.IntField(
        null=True,
        description="Response time in milliseconds for this request"
    )
    status_code = fields.IntField(
        null=True,
        description="HTTP status code if applicable"
    )

    # Token context
    input_tokens = fields.IntField(
        default=0,
        description="Input tokens used in this request"
    )
    output_tokens = fields.IntField(
        default=0,
        description="Output tokens generated in this request"
    )

    # Health context
    health_status_before = fields.CharField(
        max_length=16,
        null=True,
        description="Health status before event"
    )
    health_status_after = fields.CharField(
        max_length=16,
        null=True,
        description="Health status after event"
    )

    # Metadata
    metadata = fields.JSONField(
        default=dict,
        description="Additional event context (e.g., retry count, fallback chain)"
    )

    # Timestamp (append-only, never updated)
    created_at = fields.DatetimeField(
        auto_now_add=True,
        db_index=True,
        description="Event timestamp (immutable)"
    )

    class Meta:
        table = "api_service_events"
        table_description_plural = "API Service Events"
        table_description_singular = "API Service Event"
        # Composite index for session + timestamp queries (most common)
        indexes = [
            ("session_id", "created_at"),
            ("session_id", "event_type"),
            ("event_type", "created_at"),
        ]
        # Append-only: prevent accidental updates
        # (enforced at application layer, not DB)
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """String representation of API service event."""
        return (
            f"ApiServiceEvent("
            f"session={self.session_id}, "
            f"type={self.event_type}, "
            f"reason={self.reason}"
            f")"
        )
