"""Session investigation layer model — tracks active phase and context per session."""
from tortoise.models import Model
from tortoise import fields


class SessionLayer(Model):
    """Tracks the active investigation phase, hypotheses, and focus for a session."""
    id = fields.IntField(primary_key=True)
    session = fields.ForeignKeyField(
        "models.Session", related_name="layers", on_delete=fields.CASCADE, unique=True,
    )
    name = fields.CharField(max_length=256, default="")
    active_phase = fields.CharField(max_length=64, default="init", db_index=True)
    current_hypotheses = fields.JSONField(default=list)
    investigation_focus = fields.JSONField(default=list)
    analysis_notes = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "session_layers"
