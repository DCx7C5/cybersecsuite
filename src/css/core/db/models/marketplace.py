"""Marketplace ORM models."""

from datetime import datetime

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
from css.core.enums import MarketplaceItemType, MarketplaceStatus

from .base import BaseModel


class MarketplaceItemInfo(msgspec.Struct):
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


class BaseMarketPlace(BaseModel):
    name = NameField(max_length=255, db_index=True)
    description = DescriptionField(null=True)
    version = VersionField(max_length=20, default="0.1.0")
    remote_index_hash = SHA512SumField(null=True)
    local_index_hash = SHA512SumField(null=True)
    update_available = fields.BooleanField(default=False)
    last_index_check = fields.DatetimeField(null=True)
    status = fields.CharEnumField(MarketplaceStatus, default=MarketplaceStatus.active)

    class Meta:
        abstract = True


class MarketplaceMeta(BaseMarketPlace):
    """Tortoise ORM model for marketplace metadata."""

    class Meta:
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


class MarketplaceItem(BaseMarketPlace):
    """Tortoise ORM model for marketplace items."""
    slug = SlugField(max_length=255, unique=True, db_index=True)
    kind = CharEnumField(MarketplaceItemType, default=MarketplaceItemType.agent)
    meta = fields.JSONField(default=dict)
    install_path = PathField(max_length=512, null=True)
    source_url = UrlField(max_length=512, null=True)
    installed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def to_domain(self) -> MarketplaceItemInfo:
        """Convert ORM record to domain value type."""
        return MarketplaceItemInfo(
            id=self.id,
            name=self.name,
            description=self.description,
            slug=self.slug,
            kind=self.kind.value if hasattr(self.kind, 'value') else self.kind,
            version=self.version,
            status=self.status.value if hasattr(self.status, 'value') else self.status,
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

    class Meta:
        table = "marketplace_item"
        table_description_plural = "Marketplace Items"
        table_description_singular = "Marketplace Item"
        ordering = ("slug", "name")
        indexes = (
            Index(fields=["kind", "status"]),
            Index(fields=["kind", "version"]),
        )
        unique_together = (
            ("kind", "name"),
            ("kind", "slug"),
        )


class MarketplaceItemTag(BaseModel):
    """M2M junction table linking MarketplaceItem to Tag."""
    marketplace_item = fields.ForeignKeyField(
        "css.MarketplaceItem",
        related_name="tags_m2m"
    )
    tag = fields.ForeignKeyField(
        "css.Tag",
        related_name="marketplace_items"
    )
    # TODO: check for completeness
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
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
