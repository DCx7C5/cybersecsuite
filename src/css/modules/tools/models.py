"""Tortoise ORM models for tool persistence."""

from datetime import datetime
from typing import cast, override

import msgspec
from tortoise import fields, models

from css.core.db.fields import DescriptionField, NameField
from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin

from .enums import CompositionStrategy


class HybridToolDefinition(BaseModel, TimestampMixin):
    """Persisted hybrid tool definition in database.
    
    Maps to HybridToolSchema dataclass for runtime use.
    """
    name = NameField(max_length=256, unique=True, db_index=True)
    description = DescriptionField()
    component_tools = fields.JSONField()
    composition_strategy = fields.CharEnumField(
        CompositionStrategy,
        default=CompositionStrategy.SEQUENTIAL,
    )
    fallback_provider = fields.CharField(max_length=100, null=True)
    requires_coordination = fields.BooleanField(default=False)
    metadata = fields.JSONField(default=dict)
    enabled = fields.BooleanField(default=True)
    created_by = fields.CharField(max_length=256, null=True)
    
    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "hybrid_tool"
        ordering = ["name"]

    @override
    def __repr__(self):
        return f"<HybridToolDefinition {self.name}>"

    @override
    def __str__(self):
        return self.name


    def to_domain(self):
        """Convert ORM model to HybridToolSchema."""
        from css.modules.tools.types import HybridToolSchema
        return HybridToolSchema(
            name=self.name,
            description=self.description,
            component_tools=self.component_tools,
            composition_strategy=self.composition_strategy,
            fallback_provider=self.fallback_provider,
            requires_coordination=self.requires_coordination,
            metadata=self.metadata,
            enabled=self.enabled,
            tags=[],
        )

    to_schema = to_domain

    @staticmethod
    def from_domain(schema):
        """Create ORM model from HybridToolSchema."""
        return HybridToolDefinition(
            name=schema.name,
            description=schema.description,
            component_tools=schema.component_tools,
            composition_strategy=schema.composition_strategy,
            fallback_provider=schema.fallback_provider,
            requires_coordination=schema.requires_coordination,
            metadata=schema.metadata,
            enabled=schema.enabled,
        )

    from_schema = from_domain


class HybridToolDefinitionTagInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Domain value type for hybrid tool definition/tag relation."""

    id: int
    hybrid_tool_id: int
    tag_id: int
    created_at: datetime
    updated_at: datetime


class HybridToolDefinitionTag(BaseModel, TimestampMixin):
    """M2M junction table linking HybridToolDefinition to Tag."""

    hybrid_tool = fields.ForeignKeyField(
        "models.HybridToolDefinition",
        related_name="tags_m2m",
    )
    tag = fields.ForeignKeyField(
        "models.Tag",
        related_name="hybrid_tools",
    )

    def to_domain(self) -> HybridToolDefinitionTagInfo:
        hybrid_tool_id = cast(int, getattr(self, "hybrid_tool_id"))
        tag_id = cast(int, getattr(self, "tag_id"))
        return HybridToolDefinitionTagInfo(
            id=self.id,
            hybrid_tool_id=hybrid_tool_id,
            tag_id=tag_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, info: HybridToolDefinitionTagInfo) -> "HybridToolDefinitionTag":
        return cls(
            id=info.id,
            hybrid_tool_id=info.hybrid_tool_id,
            tag_id=info.tag_id,
        )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        table = "hybrid_tool_tag"
        table_description = "M2M junction between HybridToolDefinition and Tag"
        unique_together = (
            ("hybrid_tool_id", "tag_id"),
        )
        indexes = (
            models.Index(fields=["hybrid_tool_id", "tag_id"]),  # type: ignore[reportPrivateImportUsage]
            models.Index(fields=["tag_id", "hybrid_tool_id"]),  # type: ignore[reportPrivateImportUsage]
        )
