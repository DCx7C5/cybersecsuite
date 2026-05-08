"""Multi-orchestrator management models."""

from tortoise import fields, models

from .base import BaseModel
from .enums import OrchestratorStatus


class OrchestratorInstance(BaseModel):
    """Orchestrator instance tracking."""
    team = fields.ForeignKeyField("models.Team", related_name="orchestrator_instances", on_delete=fields.CASCADE)
    orchestrator_id = fields.CharField(max_length=128, unique=True, db_index=True)
    status = fields.CharEnumField(
        OrchestratorStatus,
        default=OrchestratorStatus.STARTING,
        db_index=True,
    )
    heartbeat_at = fields.DatetimeField(null=True)
    crashed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "orchestrator_instances"
        indexes = [models.Index(fields=["team_id", "status"])]
