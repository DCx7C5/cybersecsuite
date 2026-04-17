from tortoise import fields
from tortoise.models import Model
from db.models.enums import ProviderEnum  # falls vorhanden

class ApiUsageLog(Model):
    id = fields.UUIDField(pk=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    provider = fields.CharEnumField(ProviderEnum, default="anthropic")  # anthropic | openai | grok
    model = fields.CharField(max_length=128)
    input_tokens = fields.BigIntField()
    cache_read_input_tokens = fields.BigIntField(null=True)
    cache_creation_input_tokens = fields.BigIntField(null=True)
    output_tokens = fields.BigIntField()
    total_tokens = fields.BigIntField()
    cost_estimate = fields.DecimalField(max_digits=12, decimal_places=6, null=True)  # optional
    request_id = fields.CharField(max_length=64, null=True)
    session_id = fields.CharField(max_length=64, null=True)  # aus deiner init_session.sh
    raw_usage = fields.JSONField()
    class Meta:
        table = "api_usage_log"
        indexes = [("provider", "model", "timestamp")]
