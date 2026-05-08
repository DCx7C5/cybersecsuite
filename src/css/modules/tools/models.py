"""Tortoise ORM models for tool persistence."""

from tortoise import fields, models

from css.core.db.fields import DescriptionField, NameField
from css.core.db.models.base import BaseModel

from .enums import CompositionStrategy


class HybridToolDefinition(BaseModel):
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
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_by = fields.CharField(max_length=256, null=True)
    
    class Meta:
        table = "hybrid_tool"
        ordering = ["name"]

    def __repr__(self):
        return f"<HybridToolDefinition {self.name}>"

    def __str__(self):
        return self.name


    def to_schema(self):
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

    @staticmethod
    def from_schema(schema):
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


class HybridToolDefinitionTag(BaseModel):
    """M2M junction table linking HybridToolDefinition to Tag."""
    hybrid_tool = fields.ForeignKeyField(
        "css.HybridToolDefinition",
        related_name="tags_m2m"
    )
    tag = fields.ForeignKeyField(
        "css.Tag",
        related_name="hybrid_tools"
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "hybrid_tool_tag"
        table_description = "M2M relationship between hybrid tools and tags"
        unique_together = [("hybrid_tool", "tag")]
        indexes = [models.Index(fields=["hybrid_tool", "tag"])]
