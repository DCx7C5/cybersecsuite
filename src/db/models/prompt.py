"""Prompt model — stores reusable prompts for agents and the proxy."""
from tortoise import fields
from tortoise.models import Model


class Prompt(Model):
    """A named, versioned prompt template."""

    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    content = fields.TextField(description="The prompt text body.")
    category = fields.CharField(max_length=128, default="general", db_index=True)
    tags = fields.JSONField(default=list)
    is_active = fields.BooleanField(default=True, db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "prompts"
        table_description_plural = "Prompts"
        table_description_singular = "Prompt"
        ordering = ["name"]
        unique_together = ("name", "category")

