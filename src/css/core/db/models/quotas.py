"""Task assignment, team quota, and task result models."""

from datetime import datetime

import msgspec
from tortoise import fields
from tortoise.indexes import Index
from css.core.db.models.base import BaseModel



class TeamQuotaInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for team quota data."""
    id: int
    team_id: int
    max_concurrent_tasks: int
    max_daily_tasks: int
    cpu_quota_percent: float
    memory_quota_mb: int
    current_concurrent_tasks: int
    daily_tasks_count: int
    daily_reset_at: datetime | None


class TeamQuota(BaseModel):
    """Team resource quotas enforcement."""
    id = fields.BigIntField(primary_key=True)
    team = fields.OneToOneField(
        "models.Team",
        related_name="quota",
        on_delete=fields.CASCADE,
    )
    max_concurrent_tasks = fields.IntField(default=50)
    max_daily_tasks = fields.IntField(default=500)
    cpu_quota_percent = fields.FloatField(default=100.0)
    memory_quota_mb = fields.IntField(default=2048)
    current_concurrent_tasks = fields.IntField(default=0)
    daily_tasks_count = fields.IntField(default=0)
    daily_reset_at = fields.DatetimeField(null=True)

    def to_domain(self) -> TeamQuotaInfo:
        return TeamQuotaInfo(
            id=self.id,
            team_id=self.team_id,
            max_concurrent_tasks=self.max_concurrent_tasks,
            max_daily_tasks=self.max_daily_tasks,
            cpu_quota_percent=self.cpu_quota_percent,
            memory_quota_mb=self.memory_quota_mb,
            current_concurrent_tasks=self.current_concurrent_tasks,
            daily_tasks_count=self.daily_tasks_count,
            daily_reset_at=self.daily_reset_at,
        )

    @classmethod
    def from_domain(cls, info: TeamQuotaInfo) -> "TeamQuota":
        return cls(
            team_id=info.team_id,
            max_concurrent_tasks=info.max_concurrent_tasks,
            max_daily_tasks=info.max_daily_tasks,
            cpu_quota_percent=info.cpu_quota_percent,
            memory_quota_mb=info.memory_quota_mb,
            current_concurrent_tasks=info.current_concurrent_tasks,
            daily_tasks_count=info.daily_tasks_count,
            daily_reset_at=info.daily_reset_at,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "team_quotas"
        indexes = [
            Index(fields=["team_id"]),
        ]
