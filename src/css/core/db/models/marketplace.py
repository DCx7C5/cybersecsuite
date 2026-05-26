"""Marketplace ORM models."""

from datetime import UTC, datetime
from typing import Any, Callable

import msgspec
from tortoise import fields
from tortoise.fields import CharEnumField
from tortoise.indexes import Index

from css.core.db.fields import (
    DescriptionField,
    NameField,
    PathField,
    SHA512SumField,
    SlugField,
    UrlField,
    VersionField,
)
from css.core.enums import MarketplaceItemStatus, MarketplaceItemType, MarketplaceStatus
from . import TimestampMixin

from .base import BaseModel


class MarketplaceItemInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for marketplace item data."""
    id: int
    name: str
    description: str | None
    slug: str
    kind: str
    version: str
    status: str
    meta_data: dict
    install_path: str | None
    source_url: str | None
    installed_at: datetime | None
    update_available: bool
    created_at: datetime
    updated_at: datetime


class MarketplaceMetaInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for marketplace index metadata."""

    id: int
    name: str
    description: str | None
    version: str
    remote_index_hash: str | None
    local_index_hash: str | None
    update_available: bool
    last_index_check: datetime | None
    status: str | Any


class MarketplaceItemTagInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for marketplace item/tag relation."""

    id: int
    marketplace_item_id: int
    tag_id: int
    created_at: datetime
    updated_at: datetime


class BaseMarketPlace(BaseModel):
    name = NameField(max_length=255, db_index=True)
    description = DescriptionField(null=True)
    version = VersionField(max_length=20, default="0.1.0")
    remote_index_hash = SHA512SumField(null=True)
    local_index_hash = SHA512SumField(null=True)
    update_available = fields.BooleanField(default=False)
    last_index_check = fields.DatetimeField(null=True)
    status = fields.CharEnumField(MarketplaceStatus, default=MarketplaceStatus.active)

    @property
    def status_value(self) -> Callable[[], Any] | Callable[[], Any] | str:
        return self.status.value if hasattr(self.status, "value") else str(self.status)

    @property
    def needs_index_refresh(self) -> bool:
        return self.update_available or self.remote_index_hash != self.local_index_hash

    def mark_index_checked(
        self,
        *,
        checked_at: datetime | None = None,
        remote_index_hash: str | None = None,
        local_index_hash: str | None = None,
        update_available: bool | None = None,
    ) -> None:
        """Update index-sync metadata on the current instance."""

        self.last_index_check = checked_at or datetime.now(UTC)
        if remote_index_hash is not None:
            self.remote_index_hash = remote_index_hash
        if local_index_hash is not None:
            self.local_index_hash = local_index_hash
        if update_available is not None:
            self.update_available = update_available
        self.status = (
            MarketplaceStatus.updates_available
            if self.update_available
            else MarketplaceStatus.active
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True


class MarketplaceMetaManager:
    """Query helpers for ``MarketplaceMeta``."""

    async def by_name(self, name: str) -> "MarketplaceMeta | None":
        return await MarketplaceMeta.get_or_none(name=name)

    async def stale(self) -> list["MarketplaceMeta"]:
        return await MarketplaceMeta.filter(update_available=True).order_by("name", "id")


class MarketplaceMeta(BaseMarketPlace):
    """Tortoise ORM model for marketplace metadata."""

    manager = MarketplaceMetaManager()

    def to_domain(self) -> MarketplaceMetaInfo:
        return MarketplaceMetaInfo(
            id=self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            remote_index_hash=self.remote_index_hash,
            local_index_hash=self.local_index_hash,
            update_available=self.update_available,
            last_index_check=self.last_index_check,
            status=self.status_value,
        )

    @classmethod
    def from_domain(cls, info: MarketplaceMetaInfo) -> "MarketplaceMeta":
        return cls(
            name=info.name,
            description=info.description,
            version=info.version,
            remote_index_hash=info.remote_index_hash,
            local_index_hash=info.local_index_hash,
            update_available=info.update_available,
            last_index_check=info.last_index_check,
            status=info.status,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "marketplace_meta"
        table_verbose = "Marketplace Meta"
        table_verbose_plural = "Marketplace Meta"
        ordering = ["id", "name"]
        indexes = (
            Index(fields=["name"]),
            Index(fields=["status"]),
        )
        unique_together = (
            ("name", "version"),
        )

class MarketplaceItemManager:
    """Query helpers for ``MarketplaceItem``."""

    async def all_items(self) -> list["MarketplaceItem"]:
        return await MarketplaceItem.all().order_by("slug", "id")

    async def installed(self) -> list["MarketplaceItem"]:
        return await MarketplaceItem.filter(installed_at__not_isnull=True).all()

    async def enabled(self) -> list["MarketplaceItem"]:
        return await MarketplaceItem.filter(status=MarketplaceStatus.active).order_by("slug", "id")

    async def by_kind(self, kind: MarketplaceItemType | str) -> list["MarketplaceItem"]:
        return await MarketplaceItem.filter(kind=kind).all()

    async def by_slug(self, slug: str) -> "MarketplaceItem | None":
        return await MarketplaceItem.get_or_none(slug=slug)


class MarketplaceItem(BaseMarketPlace):
    """Tortoise ORM model for marketplace items."""
    slug = SlugField(max_length=255, unique=True, db_index=True)
    kind = CharEnumField(MarketplaceItemType, default=MarketplaceItemType.agent)
    status = fields.CharEnumField(MarketplaceItemStatus, default=MarketplaceItemStatus.enabled)
    meta = fields.JSONField(default=dict)
    install_path = PathField(max_length=512, null=True)
    source_url = UrlField(max_length=512, null=True)
    installed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    manager = MarketplaceItemManager()

    @property
    def sha512(self) -> str:
        if isinstance(self.meta, dict):
            value = self.meta.get("sha512")
            if isinstance(value, str):
                return value
        return ""

    def to_domain(self) -> MarketplaceItemInfo:
        """Convert ORM record to domain value type."""
        return MarketplaceItemInfo(
            id=self.id,
            name=self.name,
            description=self.description,
            slug=self.slug,
            kind=self.kind.value if hasattr(self.kind, 'value') else self.kind,
            version=self.version,
            status=self.status_value,
            meta_data=self.meta or {},
            install_path=self.install_path,
            source_url=self.source_url,
            installed_at=self.installed_at,
            update_available=self.update_available,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: MarketplaceItemInfo) -> "MarketplaceItem":
        """Create ORM instance from domain value type."""
        return cls(
            name=info.name,
            description=info.description,
            slug=info.slug,
            kind=info.kind,
            version=info.version,
            status=info.status,
            meta=info.meta_data,
            install_path=info.install_path,
            source_url=info.source_url,
            installed_at=info.installed_at,
            update_available=info.update_available,
        )

    @property
    def is_installed(self) -> bool:
        return self.installed_at is not None

    @property
    def has_source(self) -> bool:
        return bool(self.source_url)

    async def mark_installed(
        self,
        *,
        install_path: str,
        installed_at: datetime | None = None,
    ) -> None:
        await self.save_changes(
            install_path=install_path,
            installed_at=installed_at or datetime.now(UTC),
            update_available=False,
            status=MarketplaceItemStatus.installed,
        )

    async def mark_uninstalled(self) -> None:
        await self.save_changes(
            install_path=None,
            installed_at=None,
            status=MarketplaceItemStatus.disabled,
        )

    async def mark_update_available(self, update_available: bool = True) -> None:
        await self.save_changes(
            update_available=update_available,
            status=(
                MarketplaceItemStatus.update_available if update_available else MarketplaceItemStatus.enabled
            ),
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "marketplace_item"
        table_verbose = "Marketplace Item"
        table_verbose_plural = "Marketplace Items"
        ordering = ("slug", "name")
        indexes = (
            Index(fields=["kind", "status"]),
            Index(fields=["kind", "version"]),
        )
        unique_together = (
            ("kind", "name"),
            ("kind", "slug"),
        )


class MarketplaceItemTag(BaseModel, TimestampMixin):
    """M2M junction table linking MarketplaceItem to Tag."""
    marketplace_item = fields.ForeignKeyField(
        "css.MarketplaceItem",
        related_name="tags_m2m"
    )
    tag = fields.ForeignKeyField(
        "css.Tag",
        related_name="marketplace_items"
    )

    def to_domain(self) -> MarketplaceItemTagInfo:
        return MarketplaceItemTagInfo(
            id=self.id,
            marketplace_item_id=self.marketplace_item_id,
            tag_id=self.tag_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: MarketplaceItemTagInfo) -> "MarketplaceItemTag":
        return cls(
            marketplace_item_id=info.marketplace_item_id,
            tag_id=info.tag_id,
            created_at=info.created_at,
            updated_at=info.updated_at,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "marketplace_item_tag"
        table_verbose = "Marketplace Item Tag"
        table_verbose_plural = "Marketplace Item Tags"

        unique_together = (
            ("marketplace_item", "tag"),
        )
        indexes = (
            Index(fields=["marketplace_item", "tag"]),
            Index(fields=["tag", "marketplace_item"]),
        )
