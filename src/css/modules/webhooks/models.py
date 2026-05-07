"""Webhook endpoint and delivery models."""

from tortoise import Model, fields


class WebhookEndpoint(Model):
    """Configured outbound webhook endpoint."""

    id = fields.BigIntField(primary_key=True)
    organization: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "css.Organization",
        related_name="webhook_endpoints",
        on_delete=fields.CASCADE,
    )
    name = fields.CharField(max_length=255)
    url = fields.CharField(max_length=1024)
    secret = fields.CharField(max_length=255, default="")
    event_filter = fields.JSONField(default=list)
    retry_policy = fields.JSONField(default={"max_attempts": 3, "base_delay_seconds": 2})
    is_active = fields.BooleanField(default=True, db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "webhook_endpoints"
        unique_together = (("organization", "name"),)


class WebhookDelivery(Model):
    """Delivery attempt log for each webhook call."""

    id = fields.BigIntField(primary_key=True)
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

    class Meta:
        table = "webhook_deliveries"
        indexes = [("endpoint_id", "event_type", "dispatched_at")]
