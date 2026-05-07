from tortoise import Model, fields, models

from css.core.enums import MarketplaceItemStatus, MarketplaceItemType, MarketplaceStatus


class MarketplaceMeta(Model):
    """Tortoise ORM model for marketplace metadata."""
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=255, db_index=True)
    description = fields.TextField()
    version = fields.CharField(max_length=20, default="0.1.0")
    sha512 = fields.CharField(max_length=255, null=True)
    status = fields.CharEnumField(MarketplaceStatus, default=MarketplaceStatus.active)
    remote_index_hash = fields.CharField(max_length=512, null=True)
    local_index_hash = fields.CharField(max_length=512, null=True)
    update_available = fields.BooleanField(default=False)
    last_index_check = fields.DatetimeField(null=True)

    class Meta:
        table = "marketplace_meta"
        table_description_plural = "Marketplace Meta"
        table_description_singular = "Marketplace Meta"
        ordering = ["id", "name"]


class MarketplaceItem(Model):
    """Tortoise ORM model for marketplace items."""
    id = fields.BigIntField(primary_key=True)
    slug = fields.CharField(max_length=255, unique=True, db_index=True)
    name = fields.CharField(max_length=255, db_index=True)
    description = fields.TextField()
    kind = fields.CharEnumField(MarketplaceItemType, default=MarketplaceItemType.agent)
    version = fields.CharField(max_length=20, default="0.1.0")
    status = fields.CharEnumField(MarketplaceItemStatus, default=MarketplaceItemStatus.disabled)
    sha512 = fields.CharField(max_length=255, null=True)

    meta = fields.JSONField(default=dict)
    install_path = fields.CharField(max_length=512, null=True)
    source_url = fields.CharField(max_length=512, null=True)
    installed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "marketplace_item"
        table_description_plural = "Marketplace Items"
        table_description_singular = "Marketplace Item"
        ordering = ["slug", "name"]
        indexes = [
            models.Index(fields=["kind", "status"]),
            models.Index(fields=["kind", "version"]),
        ]
        unique_together = [("kind", "name")]


class MarketplaceItemTag(Model):
    """M2M junction table linking MarketplaceItem to Tag."""
    id = fields.BigIntField(primary_key=True)
    marketplace_item = fields.ForeignKeyField(
        "css.MarketplaceItem",
        related_name="tags_m2m"
    )
    tag = fields.ForeignKeyField(
        "css.Tag",
        related_name="marketplace_items"
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "marketplace_item_tag"
        table_description = "M2M relationship between marketplace items and tags"
        unique_together = [("marketplace_item", "tag")]
        indexes = [models.Index(fields=["marketplace_item", "tag"])]
