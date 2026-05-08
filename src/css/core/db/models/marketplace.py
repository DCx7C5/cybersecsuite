"""Marketplace ORM models."""

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
