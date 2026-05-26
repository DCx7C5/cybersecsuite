"""Webhook endpoint and delivery models."""

from tortoise import fields
from css.core.db.models.base import BaseModel
from css.core.db.fields import LabelField, UrlField
from css.core.db.models.mixins import TimestampMixin


class WebhookEndpoint(BaseModel, TimestampMixin):
    """Configured outbound webhook endpoint."""

    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="webhook_endpoints",
        on_delete=fields.CASCADE,
    )
    name = LabelField()
    url = UrlField(max_length=1024)
    secret = fields.CharField(max_length=255, default="")
    event_filter = fields.JSONField(default=list)
    retry_policy = fields.JSONField(default={"max_attempts": 3, "base_delay_seconds": 2})
    is_active = fields.BooleanField(default=True, db_index=True)
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "webhook_endpoint"
        table_verbose = "Webhook Endpoint"
        table_verbose_plural = "Webhook Endpoints"
        unique_together = (("organization", "name"),)


class WebhookDelivery(BaseModel):
    """Delivery attempt log for each webhook call."""

    endpoint: fields.ForeignKeyRelation[WebhookEndpoint] = fields.ForeignKeyField(
        "css.WebhookEndpoint",
        related_name="deliveries",
        on_delete=fields.CASCADE,
    )
    event_type = fields.CharField(max_length=128, db_index=True)
    payload = fields.JSONField(default=dict)
    attempt = fields.IntField(default=1)
    status = fields.CharField(max_length=32, default="pending", db_index=True)
    response_code = fields.IntField(null=True)
    response_body = fields.TextField(default="")
    error = fields.TextField(default="")
    dispatched_at = fields.DatetimeField(auto_now_add=True)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "webhook_delivery"
        table_verbose = "Webhook Delivery"
        table_verbose_plural = "Webhook Deliveries"
        indexes = [("endpoint_id", "event_type", "dispatched_at")]
