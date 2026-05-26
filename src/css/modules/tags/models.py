from tortoise import fields
from tortoise.indexes import Index
from css.core.db.fields import DescriptionField, LabelField, SlugField
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin
from .manager import TagManager

from .enums import TagColor


class Tag(BaseModel, TimestampMixin):
    """Reusable classification tag with optional taxonomy parent."""
    name = LabelField(db_index=True)
    slug = SlugField(max_length=128, db_index=True, default="", unique=True)
    color = fields.CharEnumField(TagColor, default=TagColor.GRAY)
    parent_tag = fields.ForeignKeyField("models.Tag", related_name="children", null=True)
    description = DescriptionField(default="")

    manager = TagManager()

    class Meta(BaseModel.Meta, TimestampMixin.Meta):
        abstract = False
        table = "tag"
        table_description = (
            "Reusable tags with optional taxonomy parent; not a navigation tree model"
        )
        ordering = ["name"]
        indexes = [
            Index(fields=["name"]),
            Index(fields=["slug"]),
            Index(fields=["parent_tag_id"]),
        ]
