"""Host model for individual systems and assets within machines."""

from datetime import datetime

import msgspec
from tortoise import fields
from tortoise.indexes import Index

from .base import BaseModel
from .mixins import TimestampMixin
from ..fields import NameField


class HostInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for host data."""

    id: int
    name: str
    machine_id: int
    ipv4_address: str | None
    ipv6_address: str | None
    fqdn: str | None
    host_role: str
    is_active: bool
    last_seen: datetime | None
    created_at: datetime
    updated_at: datetime


class HostManager:
    """Query helpers for ``Host``."""

    async def active(self) -> list["Host"]:
        return await Host.filter(is_active=True).order_by("name", "id")

    async def by_machine(self, machine_id: int) -> list["Host"]:
        return await Host.filter(machine_id=machine_id).order_by("name", "id")

    async def by_ipv4(self, ipv4_address: str) -> "Host | None":
        return await Host.get_or_none(ipv4_address=ipv4_address)

    async def by_fqdn(self, fqdn: str) -> "Host | None":
        return await Host.get_or_none(fqdn=fqdn)

    async def by_role(self, host_role: str) -> list["Host"]:
        return await Host.filter(host_role=host_role).order_by("name", "id")


class Host(BaseModel, TimestampMixin):
    """Host/asset record representing individual systems or network endpoints."""

    name = NameField(max_length=255, db_index=True)
    machine = fields.ForeignKeyField(
        "models.Machine",
        related_name="hosts",
        description="Infrastructure machine containing this host",
    )
    ipv4_address = fields.CharField(max_length=45, null=True, db_index=True)
    ipv6_address = fields.CharField(max_length=45, null=True)
    fqdn = fields.CharField(max_length=255, null=True, unique=True, db_index=True)
    host_role = fields.CharField(max_length=128, db_index=True)
    is_active = fields.BooleanField(default=True, db_index=True)
    last_seen = fields.DatetimeField(null=True)

    manager = HostManager()

    def to_domain(self) -> HostInfo:
        return HostInfo(
            id=self.id,
            name=self.name,
            machine_id=self.machine_id,  # type: ignore[reportAttributeAccessIssue]
            ipv4_address=self.ipv4_address,
            ipv6_address=self.ipv6_address,
            fqdn=self.fqdn,
            host_role=self.host_role,
            is_active=self.is_active,
            last_seen=self.last_seen,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: HostInfo) -> "Host":
        return cls(
            name=info.name,
            machine_id=info.machine_id,
            ipv4_address=info.ipv4_address,
            ipv6_address=info.ipv6_address,
            fqdn=info.fqdn,
            host_role=info.host_role,
            is_active=info.is_active,
            last_seen=info.last_seen,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "host"
        indexes = [
            Index(fields=["machine_id", "name"]),
            Index(fields=["ipv4_address", "id"]),
            Index(fields=["fqdn", "id"]),
            Index(fields=["host_role", "is_active"]),
            Index(fields=["is_active", "last_seen"]),
        ]
        ordering = ["name"]


async def sync_default_hosts() -> list["Host"]:
    """Seed localhost host on first start."""
    localhost_host = await Host.get_or_none(name="localhost")
    if localhost_host is not None:
        return [localhost_host]

    from .machine import sync_default_machines

    machines = await sync_default_machines()
    if not machines:
        return []

    localhost_host = await Host.create(
        name="localhost",
        machine_id=machines[0].id,
        ipv4_address="127.0.0.1",
        ipv6_address="::1",
        fqdn="localhost.localdomain",
        host_role="development",
        is_active=True,
    )
    return [localhost_host]
