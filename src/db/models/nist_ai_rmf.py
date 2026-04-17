"""NIST AI Risk Management Framework 1.0 control model."""

from tortoise import fields
from tortoise.models import Model


class NistAiRmfControl(Model):
    """NIST AI RMF 1.0 subcategory — 72 entries across 4 functions."""

    id = fields.IntField(primary_key=True)
    control_id = fields.CharField(max_length=32, unique=True, db_index=True)
    function = fields.CharField(max_length=16, db_index=True)   # Govern/Map/Measure/Manage
    category = fields.CharField(max_length=128, db_index=True)
    title = fields.TextField(default="")
    description = fields.TextField(default="")
    section_about = fields.TextField(default="")
    suggested_actions = fields.JSONField(default=list)          # list[str]
    ai_actors = fields.JSONField(default=list)                  # list[str]
    topic = fields.CharField(max_length=128, default="", db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "compliance_nist_ai_rmf"
        ordering = ["control_id"]
        indexes = (("function",), ("category",), ("topic",))

    def __str__(self) -> str:
        return f"{self.control_id}: {self.category}"
