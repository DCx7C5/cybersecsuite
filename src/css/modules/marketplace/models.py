from tortoise import Model, fields
from .enums import MarketplaceItemType, MarketplaceItemStatus, MarketplaceStatus


class MarketplaceMeta(Model):
    """Tortoise ORM model for marketplace metadata."""
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=255, db_index=True)
    description = fields.TextField()
    version = fields.CharField(max_length=20, default="0.1.0")
    sha512 = fields.CharField(max_length=255, null=True)
    status = fields.CharEnumField(MarketplaceStatus, default=MarketplaceStatus.active)

    class Meta:
        table = "marketplace_meta"
        table_description_plural = "Marketplace Meta"
        table_description_singular = "Marketplace Meta"
        ordering = ["id", "name"]


class MarketplaceItem(Model):
    """Tortoise ORM model for marketplace items."""
    id = fields.CharField(max_length=255, primary_key=True)
    name = fields.CharField(max_length=255, db_index=True)
    description = fields.TextField()
    kind = fields.CharEnumField(MarketplaceItemType, default=MarketplaceItemType.agent)
    version = fields.CharField(max_length=20, default="0.1.0")
    status = fields.CharEnumField(MarketplaceItemStatus, default=MarketplaceItemStatus.disabled)
    sha512 = fields.CharField(max_length=255, null=True)

    tags = fields.JSONField(default=list)
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
        ordering = ["id", "name"]
        indexes = [("kind", "status"), ("kind", "version")]
        unique_together = [("kind", "name")]


