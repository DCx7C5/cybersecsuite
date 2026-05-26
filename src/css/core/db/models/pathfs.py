"""PathFS model for filesystem monitoring and path hierarchy tracking."""

from typing import cast, override
from datetime import datetime

import msgspec
from tortoise import fields
from tortoise.indexes import Index

from .base import BaseTreeModel
from .mixins import TimestampMixin
from ..fields import NonNegativeIntField


class PathFSInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for filesystem path data."""

    id: int
    host_id: int
    path: str
    path_type: str
    parent_id: int | None
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

    async def roots(self, host_id: int) -> list["PathFS"]:
        return await PathFS.filter(host_id=host_id, parent_id=None).order_by("path", "id")

    async def monitored_paths(self) -> list["PathFS"]:
        return await PathFS.filter(
            is_monitored=True,
        ).order_by("host_id", "path", "id")


class PathFS(BaseTreeModel, TimestampMixin):
    """Filesystem path record for monitoring file/directory hierarchy and metadata."""

    host = fields.ForeignKeyField(
        "models.Host",
        related_name="paths",
        description="Host containing this filesystem path",
    )
    path = fields.CharField(max_length=1024, db_index=True)
    path_type = fields.CharField(max_length=64, db_index=True)
    file_size = NonNegativeIntField(default=0)
    is_monitored = fields.BooleanField(default=True, db_index=True)
    last_scanned = fields.DatetimeField(null=True)

    manager = PathFSManager()

    def to_domain(self) -> PathFSInfo:
        parent_id: int | None = getattr(self, "parent_id", None)
        return PathFSInfo(
            id=self.id,
            host_id=self.host_id,  # type: ignore[reportAttributeAccessIssue]
            path=self.path,
            path_type=self.path_type,
            parent_id=parent_id,
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
            parent_id=info.parent_id,
            file_size=info.file_size,
            is_monitored=info.is_monitored,
            last_scanned=info.last_scanned,
        )

    @override
    async def ordered_children(self) -> list["PathFS"]:  # type: ignore[reportIncompatibleMethodOverride]
        """Load direct children in stable order by path."""

        parent_id: int | None = getattr(self, "parent_id", None)
        return cast(list["PathFS"], await type(self).filter(parent_id=parent_id).order_by("path", "id"))

    @override
    async def siblings(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        *,
        include_self: bool = False,
    ) -> list["PathFS"]:
        """Load sibling paths in display order."""

        parent_id: int | None = getattr(self, "parent_id", None)
        items = cast(
            list["PathFS"],
            await type(self).filter(parent_id=parent_id).order_by("path", "id"),
        )
        if include_self:
            return items
        return [item for item in items if item.id != self.id]

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "path_fs"
        unique_together = [("host_id", "path")]
        indexes = [
            Index(fields=["host_id", "path"]),
            Index(fields=["host_id", "path_type"]),
            Index(fields=["parent_id", "path"]),
            Index(fields=["is_monitored", "last_scanned"]),
        ]
        ordering = ["host_id", "path"]


async def sync_default_paths() -> list["PathFS"]:
    """Seed common localhost paths on first start."""
    from .host import sync_default_hosts

    hosts = await sync_default_hosts()
    if not hosts:
        return []

    host = hosts[0]
    common_paths = [
        ("/", "directory"),
        ("/home", "directory"),
        ("/tmp", "directory"),
        ("/var", "directory"),
        ("/etc", "directory"),
    ]

    existing = await PathFS.filter(host_id=host.id)
    existing_paths = {p.path for p in existing}

    created = []
    for path, path_type in common_paths:
        if path in existing_paths:
            continue
        item = await PathFS.create(
            host_id=host.id,
            path=path,
            path_type=path_type,
            is_monitored=True,
        )
        created.append(item)

    return created if created else existing
