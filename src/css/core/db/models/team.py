"""TeamScope ORM model and team-level query helpers."""

from datetime import UTC, datetime
from typing import cast

import msgspec
from tortoise import fields
from tortoise.expressions import F
from tortoise.indexes import Index

from css.core.db.fields import LabelField
from css.modules.teams.enums import OrchestratorMode, TeamStatus

from .base import BaseModel


class TeamInfo(msgspec.Struct, frozen=True, kw_only=True):
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
    updated_at: datetime
    paused_at: datetime | None


class TeamManager:
    """Query helpers for ``Team``."""

    async def active(self) -> list["Team"]:
        return await Team.filter(status=TeamStatus.ACTIVE).order_by("team_name", "id")

    async def by_session(self, session_id: int) -> list["Team"]:
        return await Team.filter(session_id=session_id).order_by("team_name", "id")

    async def by_status(self, status: TeamStatus) -> list["Team"]:
        return await Team.filter(status=status).order_by("team_name", "id")

    async def with_orchestrator_capacity(self) -> list["Team"]:
        return await Team.filter(
            status=TeamStatus.ACTIVE,
            current_orchestrators__lt=F("max_orchestrators"),
        ).order_by("current_orchestrators", "team_name", "id")


class Team(BaseModel):
    """Team scope — isolated team context with orchestrator pool and task queue."""

    session = fields.ForeignKeyField(
        "models.SessionScope",
        related_name="teams",
        on_delete=fields.CASCADE,
        db_index=True,
    )
    team_name = LabelField(max_length=256, db_index=True)
    status = fields.CharEnumField(TeamStatus, default=TeamStatus.PENDING, db_index=True)
    orchestrator_mode = fields.CharEnumField(
        OrchestratorMode,
        default=OrchestratorMode.ROUND_ROBIN,
        db_index=True,
    )
    max_orchestrators = fields.IntField(default=5)
    current_orchestrators = fields.IntField(default=0)
    max_tasks = fields.IntField(default=100)
    completed_tasks = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    paused_at = fields.DatetimeField(null=True)

    manager = TeamManager()

    def to_domain(self) -> TeamInfo:
        """Convert ORM record to domain value type."""

        session_id = cast(int, getattr(self, "session_id"))
        return TeamInfo(
            id=self.id,
            session_id=session_id,
            team_name=self.team_name,
            status=self.status.value if hasattr(self.status, "value") else str(self.status),
            orchestrator_mode=(
                self.orchestrator_mode.value
                if hasattr(self.orchestrator_mode, "value")
                else str(self.orchestrator_mode)
            ),
            max_orchestrators=self.max_orchestrators,
            current_orchestrators=self.current_orchestrators,
            max_tasks=self.max_tasks,
            completed_tasks=self.completed_tasks,
            created_at=self.created_at,
            updated_at=self.updated_at,
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
            paused_at=info.paused_at,
        )

    @property
    def is_active(self) -> bool:
        return self.status == TeamStatus.ACTIVE

    @property
    def is_paused(self) -> bool:
        return self.status == TeamStatus.PAUSED

    @property
    def available_orchestrator_slots(self) -> int:
        return max(0, self.max_orchestrators - self.current_orchestrators)

    def can_spawn_orchestrator(self) -> bool:
        return self.is_active and self.available_orchestrator_slots > 0

    async def activate(self) -> None:
        """Mark the team active."""

        await self.save_changes(
            status=TeamStatus.ACTIVE,
            paused_at=None,
            updated_at=datetime.now(UTC),
        )

    async def pause(self) -> None:
        """Pause the team and record when that happened."""

        await self.save_changes(
            status=TeamStatus.PAUSED,
            paused_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def resume(self) -> None:
        """Resume a paused team."""

        await self.save_changes(
            status=TeamStatus.ACTIVE,
            paused_at=None,
            updated_at=datetime.now(UTC),
        )

    async def mark_completed(self) -> None:
        """Mark the team complete and release orchestrator activity."""

        await self.save_changes(
            status=TeamStatus.COMPLETED,
            current_orchestrators=0,
            paused_at=None,
            updated_at=datetime.now(UTC),
        )

    async def claim_orchestrator_slot(self) -> bool:
        """Reserve one orchestrator slot if capacity remains."""

        if not self.can_spawn_orchestrator():
            return False
        await self.save_changes(
            current_orchestrators=self.current_orchestrators + 1,
            updated_at=datetime.now(UTC),
        )
        return True

    async def release_orchestrator_slot(self) -> None:
        """Release one active orchestrator slot."""

        next_count = max(0, self.current_orchestrators - 1)
        await self.save_changes(
            current_orchestrators=next_count,
            updated_at=datetime.now(UTC),
        )

    async def record_completed_task(self, count: int = 1) -> None:
        """Increment completed task count."""

        await self.save_changes(
            completed_tasks=self.completed_tasks + max(0, count),
            updated_at=datetime.now(UTC),
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "teams"
        table_verbose = "Team"
        table_verbose_plural = "Teams"
        ordering = ["team_name", "id"]
        indexes = [
            Index(fields=["session_id", "team_name"]),
            Index(fields=["status", "current_orchestrators"]),
            Index(fields=["status", "paused_at"]),
        ]
        unique_together = (("session_id", "team_name"),)
