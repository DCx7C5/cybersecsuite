"""API service provider registry — maps provider names to credential accounts."""

from typing import override
from tortoise import fields

from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin


class ApiServiceProvider(BaseModel, TimestampMixin):
    """Registry entry for an external AI/API provider (e.g. openai, anthropic)."""

    name = fields.CharField(max_length=255, unique=True, db_index=True)
    display_name = fields.CharField(max_length=255, default="")
    enabled = fields.BooleanField(default=True)

    class Meta:
        table = "api_service_provider"
        ordering = ["name"]

    @override
    def __str__(self) -> str:
        return self.name
