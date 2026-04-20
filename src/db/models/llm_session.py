from tortoise import fields
from tortoise.models import Model


class LlmSession(Model):
    """One row per git-worktree lifecycle — tracks LLM API cost and token usage.

    Distinct from :class:`db.models.scope.Session` (forensic root) and
    :class:`db.models.forensic.ForensicSession` (investigation phase).

    Written via raw asyncpg in ``src/llm/db.py`` so that CLI tooling can
    record usage outside the ASGI/Tortoise ORM context (e.g., pre-commit hooks,
    standalone scripts).  The ``sid`` is a 12-character hex string derived from
    the git worktree identity, not a UUID.
    """

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
