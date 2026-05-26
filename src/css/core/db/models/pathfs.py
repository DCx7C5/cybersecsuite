"""PathFS model for filesystem monitoring and path hierarchy tracking."""

from datetime import datetime

import msgspec
from tortoise import fields
from tortoise.indexes import Index

from .base import BaseModel
from .mixins import TimestampMixin
from ..fields import NonNegativeIntField


class PathFSInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for filesystem path data."""

    id: int
    host_id: int
    path: str
    path_type: str
    parent_path_id: int | None
    file_size: int
    is_monitored: bool
    last_scanned: datetime | None
    created_at: datetime
    updated_at: datetime


class PathFSManager:
    """Query helpers for ``PathFS``."""

    async def active(self) -> list["PathFS"]:
        return await PathFS.filter(is_monitored=True).order_by("host_id", "path", "id")

    async def by_host(self, host_id: int) -> list["PathFS"]:
        return await PathFS.filter(host_id=host_id).order_by("path", "id")

    async def by_path(self, host_id: int, path: str) -> "PathFS | None":
        return await PathFS.get_or_none(host_id=host_id, path=path)

    async def by_type(self, path_type: str) -> list["PathFS"]:
        return await PathFS.filter(path_type=path_type).order_by("host_id", "path", "id")

    async def children_of(self, parent_path_id: int) -> list["PathFS"]:
        return await PathFS.filter(parent_path_id=parent_path_id).order_by("path", "id")

    async def monitored_paths(self) -> list["PathFS"]:
        return await PathFS.filter(
            is_monitored=True,
        ).order_by("host_id", "path", "id")


class PathFS(BaseModel, TimestampMixin):
    """Filesystem path record for monitoring file/directory hierarchy and metadata."""

    host = fields.ForeignKeyField(
        "models.Host",
        related_name="paths",
        description="Host containing this filesystem path",
    )
    path = fields.CharField(max_length=1024, db_index=True)
    path_type = fields.CharField(max_length=64, db_index=True)
    parent_path = fields.ForeignKeyField(
        "models.PathFS",
        on_delete=fields.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        description="Parent path in hierarchy",
    )
    file_size = NonNegativeIntField(default=0)
    is_monitored = fields.BooleanField(default=True, db_index=True)
    last_scanned = fields.DatetimeField(null=True)

    manager = PathFSManager()

    def to_domain(self) -> PathFSInfo:
        return PathFSInfo(
            id=self.id,
            host_id=self.host_id,  # type: ignore[reportAttributeAccessIssue]
            path=self.path,
            path_type=self.path_type,
            parent_path_id=self.parent_path_id,  # type: ignore[reportAttributeAccessIssue]
            file_size=self.file_size,
            is_monitored=self.is_monitored,
            last_scanned=self.last_scanned,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: PathFSInfo) -> "PathFS":
        return cls(
            host_id=info.host_id,
            path=info.path,
            path_type=info.path_type,
            parent_path_id=info.parent_path_id,
            file_size=info.file_size,
            is_monitored=info.is_monitored,
            last_scanned=info.last_scanned,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "path_fs"
        unique_together = [("host_id", "path")]
        indexes = [
            Index(fields=["host_id", "path"]),
            Index(fields=["host_id", "path_type"]),
            Index(fields=["parent_path_id", "path"]),
            Index(fields=["is_monitored", "last_scanned"]),
        ]
        ordering = ["host_id", "path"]
