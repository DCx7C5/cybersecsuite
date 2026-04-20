from tortoise import fields
from tortoise.models import Model


class LlmSession(Model):
    """One row per worktree session lifecycle."""

    sid = fields.CharField(max_length=12, pk=True)
    repo_root = fields.CharField(max_length=512, default="")
    branch = fields.CharField(max_length=256, default="")
    opened_at = fields.DatetimeField()
    closed_at = fields.DatetimeField(null=True)
    total_input_tokens = fields.BigIntField(default=0)
    total_output_tokens = fields.BigIntField(default=0)
    total_cost_usd = fields.DecimalField(max_digits=14, decimal_places=8, default=0)
    total_calls = fields.IntField(default=0)

    class Meta:
        table = "llm_sessions"
