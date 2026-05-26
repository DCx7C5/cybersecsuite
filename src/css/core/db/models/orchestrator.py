"""Multi-orchestrator tracking model and query helpers."""

from datetime import UTC, datetime, timedelta

import msgspec
from tortoise import fields, models

from .base import BaseModel
from .enums import OrchestratorStatus


class OrchestratorInstanceInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for orchestrator instance data."""

    id: int
    team_id: int
    orchestrator_id: str
    status: str
    heartbeat_at: datetime | None
    crashed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class OrchestratorInstanceManager:
    """Query helpers for ``OrchestratorInstance``."""

    async def for_team(self, team_id: int) -> list["OrchestratorInstance"]:
        return await OrchestratorInstance.filter(team_id=team_id).order_by("created_at", "id")

    async def active(self) -> list["OrchestratorInstance"]:
        return await OrchestratorInstance.exclude(
            status__in=[OrchestratorStatus.STOPPED, OrchestratorStatus.CRASHED]
        ).order_by("team_id", "orchestrator_id")

    async def by_status(self, status: OrchestratorStatus) -> list["OrchestratorInstance"]:
        return await OrchestratorInstance.filter(status=status).order_by("team_id", "orchestrator_id")

    async def stale(self, older_than_seconds: int = 300) -> list["OrchestratorInstance"]:
        cutoff = datetime.now(UTC) - timedelta(seconds=older_than_seconds)
        return await OrchestratorInstance.filter(
            heartbeat_at__not_isnull=True,
            heartbeat_at__lt=cutoff,
        ).exclude(status=OrchestratorStatus.CRASHED).order_by("heartbeat_at", "id")


class OrchestratorInstance(BaseModel):
    """One running orchestrator process assigned to a team."""

    team = fields.ForeignKeyField(
        "models.Team",
        related_name="orchestrator_instances",
        on_delete=fields.CASCADE,
    )
    orchestrator_id = fields.CharField(max_length=128, unique=True, db_index=True)
    status = fields.CharEnumField(
        OrchestratorStatus,
        default=OrchestratorStatus.STARTING,
        db_index=True,
    )
    heartbeat_at = fields.DatetimeField(null=True)
    crashed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    manager = OrchestratorInstanceManager()

    def to_domain(self) -> OrchestratorInstanceInfo:
        return OrchestratorInstanceInfo(
            id=self.id,
            team_id=self.team_id,
            orchestrator_id=self.orchestrator_id,
            status=self.status.value if hasattr(self.status, "value") else str(self.status),
            heartbeat_at=self.heartbeat_at,
            crashed_at=self.crashed_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
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

    @property
    def is_live(self) -> bool:
        return self.status not in {OrchestratorStatus.STOPPED, OrchestratorStatus.CRASHED}

    @property
    def is_available(self) -> bool:
        return self.status == OrchestratorStatus.IDLE

    async def mark_heartbeat(self, when: datetime | None = None) -> None:
        await self.save_changes(
            heartbeat_at=when or datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def mark_idle(self) -> None:
        await self.save_changes(status=OrchestratorStatus.IDLE, updated_at=datetime.now(UTC))

    async def mark_busy(self) -> None:
        await self.save_changes(status=OrchestratorStatus.BUSY, updated_at=datetime.now(UTC))

    async def mark_paused(self) -> None:
        await self.save_changes(status=OrchestratorStatus.PAUSED, updated_at=datetime.now(UTC))

    async def mark_stopped(self) -> None:
        await self.save_changes(status=OrchestratorStatus.STOPPED, updated_at=datetime.now(UTC))

    async def mark_crashed(self, when: datetime | None = None) -> None:
        crash_time = when or datetime.now(UTC)
        await self.save_changes(
            status=OrchestratorStatus.CRASHED,
            crashed_at=crash_time,
            updated_at=crash_time,
        )

    def heartbeat_is_stale(self, older_than_seconds: int = 300) -> bool:
        if self.heartbeat_at is None:
            return False
        cutoff = datetime.now(UTC) - timedelta(seconds=older_than_seconds)
        return self.heartbeat_at < cutoff

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "orchestrator_instances"
        ordering = ["team_id", "orchestrator_id"]
        indexes = [
            models.Index(fields=["team_id", "status"]),
            models.Index(fields=["status", "heartbeat_at"]),
            models.Index(fields=["orchestrator_id"]),
        ]
