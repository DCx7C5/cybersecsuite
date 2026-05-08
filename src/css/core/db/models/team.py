"""TeamScope model — team isolation, orchestrator pool, task queues, resource quotas."""

from datetime import datetime

import msgspec
from tortoise import fields, models

from css.core.db.models.base import BaseModel
from .enums import TeamStatus


class TeamInfo(msgspec.Struct):
    """Domain value type for team data."""
    id: int
    session_id: int
    team_name: str
    status: str
    orchestrator_mode: str
    max_orchestrators: int
    current_orchestrators: int
    max_tasks: int
    completed_tasks: int
    created_at: datetime
    paused_at: datetime | None


class Team(BaseModel):
    """Team scope — isolated team context with orchestrator pool and task queue.
    
    Fields:
        id: BigInt PK
        session_id: FK to SessionScope (parent)
        team_name: Team name (unique per session)
        status: one of (pending, active, paused, completed)
        orchestrator_mode: Strategy for task distribution (round-robin, least-busy, weighted)
        max_orchestrators: Pool size limit
        current_orchestrators: Active orchestrators in pool
        max_tasks: Task queue limit
        completed_tasks: Successfully completed tasks count
        created_at: Creation timestamp
        paused_at: Pause timestamp (null if active)
    """
    id = fields.BigIntField(primary_key=True)
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="teams",
        on_delete=fields.CASCADE,
        db_index=True,
    )
    team_name = fields.CharField(max_length=256, db_index=True)
    status = fields.CharEnumField(
        TeamStatus,
        default=TeamStatus.PENDING,
        db_index=True,
        description="Status: pending, active, paused, completed",
    )
    orchestrator_mode = fields.CharField(
        max_length=32,
        default="round-robin",
        description="Orchestrator selection strategy",
    )
    max_orchestrators = fields.IntField(default=5)
    current_orchestrators = fields.IntField(default=0)
    max_tasks = fields.IntField(default=100)
    completed_tasks = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    paused_at = fields.DatetimeField(null=True)

    def to_domain(self) -> TeamInfo:
        """Convert ORM record to domain value type."""
        return TeamInfo(
            id=self.id,
            session_id=self.session_id,
            team_name=self.team_name,
            status=self.status.value if hasattr(self.status, 'value') else self.status,
            orchestrator_mode=self.orchestrator_mode,
            max_orchestrators=self.max_orchestrators,
            current_orchestrators=self.current_orchestrators,
            max_tasks=self.max_tasks,
            completed_tasks=self.completed_tasks,
            created_at=self.created_at,
            paused_at=self.paused_at,
        )

    @classmethod
    def from_domain(cls, info: TeamInfo) -> "Team":
        """Create ORM instance from domain value type."""
        return cls(
            session_id=info.session_id,
            team_name=info.team_name,
            status=info.status,
            orchestrator_mode=info.orchestrator_mode,
            max_orchestrators=info.max_orchestrators,
            current_orchestrators=info.current_orchestrators,
            max_tasks=info.max_tasks,
            completed_tasks=info.completed_tasks,
            created_at=info.created_at,
            paused_at=info.paused_at,
        )

    class Meta:
        table = "teams"
        table_description_singular = "Team"
        table_description_plural = "Teams"
        indexes = [
            models.Index(fields=["session_id", "team_name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]
        unique_together = [["session_id", "team_name"]]
