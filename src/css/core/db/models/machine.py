"""Machine/endpoint infrastructure model for device/infrastructure tracking."""

from datetime import datetime

import msgspec
from tortoise import fields
from tortoise.indexes import Index

from .base import BaseModel
from .mixins import TimestampMixin
from ..fields import NameField, NonNegativeIntField, VersionField, SHA512SumField


class MachineInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for machine data."""

    id: int
    name: str
    hostname: str
    os_type: str
    os_version: str | None
    machine_uuid: str
    is_active: bool
    last_seen: datetime | None
    cpu_cores: int
    memory_gb: int
    created_at: datetime
    updated_at: datetime


class MachineManager:
    """Query helpers for ``Machine``."""

    async def active(self) -> list["Machine"]:
        return await Machine.filter(is_active=True).order_by("hostname", "id")

    async def by_hostname(self, hostname: str) -> "Machine | None":
        return await Machine.get_or_none(hostname=hostname)

    async def by_uuid(self, machine_uuid: str) -> "Machine | None":
        return await Machine.get_or_none(machine_uuid=machine_uuid)

    async def by_os_type(self, os_type: str) -> list["Machine"]:
        return await Machine.filter(os_type=os_type).order_by("hostname", "id")

    async def inactive_machines(self) -> list["Machine"]:
        return await Machine.filter(is_active=False).order_by("hostname", "id")


class Machine(BaseModel, TimestampMixin):
    """Infrastructure machine/endpoint record for monitoring and orchestration."""

    name = NameField(max_length=255, db_index=True)
    hostname = fields.CharField(max_length=255, unique=True, db_index=True)
    os_type = fields.CharField(max_length=64, db_index=True)
    os_version = VersionField(null=True)
    machine_uuid = SHA512SumField(unique=True, db_index=True)
    is_active = fields.BooleanField(default=True, db_index=True)
    last_seen = fields.DatetimeField(null=True)
    cpu_cores = NonNegativeIntField(default=1)
    memory_gb = NonNegativeIntField(default=0)

    manager = MachineManager()

    def to_domain(self) -> MachineInfo:
        return MachineInfo(
            id=self.id,
            name=self.name,
            hostname=self.hostname,
            os_type=self.os_type,
            os_version=self.os_version,
            machine_uuid=self.machine_uuid,
            is_active=self.is_active,
            last_seen=self.last_seen,
            cpu_cores=self.cpu_cores,
            memory_gb=self.memory_gb,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: MachineInfo) -> "Machine":
        return cls(
            name=info.name,
            hostname=info.hostname,
            os_type=info.os_type,
            os_version=info.os_version,
            machine_uuid=info.machine_uuid,
            is_active=info.is_active,
            last_seen=info.last_seen,
            cpu_cores=info.cpu_cores,
            memory_gb=info.memory_gb,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "machine"
        indexes = [
            Index(fields=["hostname", "id"]),
            Index(fields=["machine_uuid", "id"]),
            Index(fields=["os_type", "is_active"]),
            Index(fields=["is_active", "last_seen"]),
        ]
        ordering = ["hostname"]


async def sync_default_machines() -> list["Machine"]:
    """Seed localhost machine on first start."""
    localhost = await Machine.get_or_none(hostname="localhost")
    if localhost is not None:
        return [localhost]

    import platform
    import uuid

    localhost = await Machine.create(
        name="localhost",
        hostname="localhost",
        os_type=platform.system(),
        os_version=platform.release(),
        machine_uuid=str(uuid.getnode()),
        is_active=True,
        cpu_cores=1,
        memory_gb=0,
    )
    return [localhost]
