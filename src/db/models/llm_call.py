from tortoise import fields
from tortoise.models import Model


class LlmCall(Model):
    """One row per Anthropic API call, bound to a worktree session."""

    id = fields.BigIntField(pk=True, generated=True)
    sid = fields.CharField(max_length=12, db_index=True)
    model = fields.CharField(max_length=128)
    input_tokens = fields.IntField(default=0)
    output_tokens = fields.IntField(default=0)
    cache_read_tokens = fields.IntField(default=0)
    cache_write_tokens = fields.IntField(default=0)
    cost_usd = fields.DecimalField(max_digits=14, decimal_places=8, default=0)
    latency_ms = fields.FloatField(default=0)
    stream = fields.BooleanField(default=True)
    success = fields.BooleanField(default=True)
    error = fields.TextField(null=True)
    request_id = fields.CharField(max_length=64, null=True)
    called_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "llm_calls"
        indexes = [("sid", "called_at"), ("model", "called_at")]
