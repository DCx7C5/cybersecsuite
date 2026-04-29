"""
Generic tagging system.
"""
from tortoise.models import Model
from tortoise import fields

from db.models.enums import TagColor


class Tag(Model):
    """Reusable tag that can be applied to any entity."""
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=128, db_index=True)
    slug = fields.CharField(max_length=128, db_index=True, default="", unique=True)
    color = fields.CharEnumField(TagColor, default=TagColor.GRAY)
    description = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tags"
        table_description_plural = "Tags"
        table_description_singular = "Tag"
        ordering = ["name"]

