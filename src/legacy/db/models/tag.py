"""
Generic tagging system.
"""
from css.core.db.models.base import BaseModel
from tortoise import fields

from css.core.db.fields import DescriptionField, SlugField
from db.models.enums import TagColor


class Tag(BaseModel):
    """Reusable tag that can be applied to any entity."""
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=128, db_index=True)
    slug = SlugField(max_length=128, db_index=True, default="", unique=True)
    color = fields.CharEnumField(TagColor, default=TagColor.GRAY)
    description = DescriptionField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tags"
        table_description_plural = "Tags"
        table_description_singular = "Tag"
        ordering = ["name"]
