"""ApiUsageLog — per-request token/cost/latency record."""

from typing import override

from tortoise import fields

from .base import BaseModel
from .mixins import TimestampMixin


class ApiUsageLog(BaseModel, TimestampMixin):
    """Per-request usage record for analytics and billing."""

    provider_id = fields.CharField(max_length=128, db_index=True)
    model_id = fields.CharField(max_length=256, db_index=True)
    prompt_tokens = fields.IntField(default=0)
    completion_tokens = fields.IntField(default=0)
    cost_usd = fields.FloatField(default=0.0)
    latency_ms = fields.FloatField(default=0.0)
    stream = fields.BooleanField(default=False)
    success = fields.BooleanField(default=True, db_index=True)
    error = fields.TextField(null=True)
    request_id = fields.CharField(max_length=255, null=True, db_index=True)

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "api_usage_log"
        ordering = ["-created_at"]

    @override
    def __str__(self) -> str:
        return f"{self.provider_id}/{self.model_id} @ {self.created_at}"
