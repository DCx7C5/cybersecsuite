"""
Generic tagging system.
"""
from tortoise.models import Model
from tortoise import fields

from db.models.enums import TagColor


class Tag(Model):
    """Reusable tag that can be applied to any entity."""
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=128, db_index=True)
    slug = fields.CharField(max_length=128, db_index=True, default="")
    color = fields.CharEnumField(TagColor, default=TagColor.GRAY)
    description = fields.TextField(default="")
    workspace = fields.ForeignKeyField("models.Workspace", related_name="tags", null=True, on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tags"
        ordering = ["name"]
        unique_together = [("workspace", "slug")]
