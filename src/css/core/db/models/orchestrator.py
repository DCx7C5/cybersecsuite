"""Multi-orchestrator management models."""

from datetime import datetime

import msgspec
from tortoise import fields, models

from .base import BaseModel
from .enums import OrchestratorStatus


class OrchestratorInstanceInfo(msgspec.Struct):
    """Domain value type for orchestrator instance data."""
    id: int
    team_id: int
    orchestrator_id: str
    status: str
    heartbeat_at: datetime | None
    crashed_at: datetime | None
    created_at: datetime


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

    def to_domain(self) -> OrchestratorInstanceInfo:
        return OrchestratorInstanceInfo(
            id=self.id,
            team_id=self.team_id,
            orchestrator_id=self.orchestrator_id,
            status=self.status.value if hasattr(self.status, 'value') else self.status,
            heartbeat_at=self.heartbeat_at,
            crashed_at=self.crashed_at,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, info: OrchestratorInstanceInfo) -> "OrchestratorInstance":
        return cls(
            team_id=info.team_id,
            orchestrator_id=info.orchestrator_id,
            status=info.status,
            heartbeat_at=info.heartbeat_at,
            crashed_at=info.crashed_at,
        )

    class Meta:
        table = "orchestrator_instances"
        indexes = [models.Index(fields=["team_id", "status"])]
