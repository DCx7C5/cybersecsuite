from tortoise import fields, models
from css.core.db.fields import DescriptionField, LabelField, SlugField
from css.core.db.models.base import BaseModel

from .enums import TagColor


class Tag(BaseModel):
    """Reusable tag that can be applied to any entity."""
    name = LabelField(db_index=True)
    slug = SlugField(max_length=128, db_index=True, default="", unique=True)
    color = fields.CharEnumField(TagColor, default=TagColor.GRAY)
    parent_tag = fields.ForeignKeyField("models.Tag", related_name="children", null=True)
    description = DescriptionField(default="")
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
