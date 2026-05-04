"""Tortoise ORM models for tool persistence (database layer).

Complements types.py dataclasses with database persistence.
Follows hybrid pattern: dataclass (runtime) + ORM model (persistence).
"""

from tortoise import fields
from tortoise.models import Model


class HybridToolDefinition(Model):
    """Persisted hybrid tool definition in database.
    
    Maps to HybridToolSchema dataclass for runtime use.
    """
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256, unique=True, db_index=True)
    description = fields.TextField()
    component_tools = fields.JSONField()
    composition_strategy = fields.CharField(
        max_length=50,
        choices=[
            ("sequential", "Sequential"),
            ("parallel", "Parallel"),
            ("conditional", "Conditional"),
            ("fallback", "Fallback"),
            ("load_balanced", "Load Balanced"),
        ]
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
        """Convert ORM model to HybridToolSchema dataclass."""
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
        """Create ORM model from HybridToolSchema dataclass."""
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


class HybridToolDefinitionTag(Model):
    """M2M junction table linking HybridToolDefinition to Tag."""
    id = fields.BigIntField(primary_key=True)
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
        indexes = [("hybrid_tool", "tag")]
