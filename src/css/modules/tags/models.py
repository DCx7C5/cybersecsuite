from tortoise import fields, models
from tortoise.models import Model

from .enums import TagColor


class Tag(Model):
    """Reusable tag that can be applied to any entity."""
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=128, db_index=True)
    slug = fields.CharField(max_length=128, db_index=True, default="", unique=True)
    color = fields.CharEnumField(TagColor, default=TagColor.GRAY)
    parent_tag = fields.ForeignKeyField("models.Tag", related_name="children", null=True)
    description = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tag"
        table_description = "Reusable tags with optional hierarchy parent"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["parent_tag"]),
        ]
