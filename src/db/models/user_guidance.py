"""
User guidance models — session-scoped rules and suggestions.

UserRule follows netfilter/iptables semantics: the lower the index,
the higher the rule priority.  Rules are evaluated top-down per chain;
the first match wins.

UserSuggestion stores free-form context the operator feeds into a
session (words, sentences, paragraphs) with an optional weight.
"""
from tortoise import fields
from tortoise.models import Model

from db.models.enums import RuleChain, RuleAction, SuggestionCategory


class UserRule(Model):
    """Session-scoped rule evaluated like a netfilter chain entry.

    Lower ``index`` = higher priority.  Rules in the same chain are
    walked in ascending index order; the first match determines the
    action.  Semantics mirror iptables: chain → match → target.
    """
    id = fields.IntField(primary_key=True)
    session = fields.ForeignKeyField(
        "models.Session", related_name="user_rules",
        on_delete=fields.CASCADE, db_index=True,
    )

    # ── position & chain ──
    index = fields.IntField(
        db_index=True,
        description="Priority index — lower value = higher priority (like iptables).",
    )
    chain = fields.CharEnumField(
        RuleChain, db_index=True,
        description="Control point where this rule is evaluated.",
    )

    # ── match criteria ──
    target_pattern = fields.CharField(
        max_length=500,
        description="Glob or regex pattern to match against (tool name, path, agent, etc.).",
    )
    match_field = fields.CharField(
        max_length=100, default="",
        description="What target_pattern applies to, e.g. 'tool', 'path', 'agent', 'content'.",
    )
    condition = fields.JSONField(
        default=dict,
        description="Optional extended match conditions (key-value filters).",
    )

    # ── action ──
    action = fields.CharEnumField(
        RuleAction,
        description="Action taken when this rule matches.",
    )

    # ── metadata ──
    description = fields.TextField(default="")
    enabled = fields.BooleanField(default=True, db_index=True)
    hit_count = fields.IntField(default=0, description="How often this rule matched.")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_rules"
        ordering = ["index"]
        unique_together = [("session_id", "index")]
        indexes = [
            ("session_id", "chain"),
            ("session_id", "enabled"),
        ]

    def __str__(self):
        return f"Rule #{self.index} [{self.chain}] {self.action} → {self.target_pattern}"


class UserSuggestion(Model):
    """Free-form context the operator adds to a session.

    Can be anything: a sentence, a keyword, a paragraph.
    The optional ``weight`` lets the user signal relative importance
    (higher = more important, default 1.0).
    """
    id = fields.IntField(primary_key=True)
    session = fields.ForeignKeyField(
        "models.Session", related_name="user_suggestions",
        on_delete=fields.CASCADE, db_index=True,
    )

    content = fields.TextField(description="The suggestion text — words, sentences, etc.")
    category = fields.CharEnumField(
        SuggestionCategory, default=SuggestionCategory.CONTEXT,
        db_index=True,
        description="Kind of suggestion.",
    )
    weight = fields.FloatField(
        default=1.0,
        description="Relative importance — higher means more important. Not mandatory.",
    )

    enabled = fields.BooleanField(default=True, db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_suggestions"
        ordering = ["-weight", "-created_at"]
        indexes = [
            ("session_id", "category"),
            ("session_id", "enabled"),
        ]

    def __str__(self):
        preview = self.content[:60] + "…" if len(self.content) > 60 else self.content
        return f"Suggestion({self.category}: {preview})"

