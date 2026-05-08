"""Marketplace models for asset and MCP tracking."""
from tortoise import fields
from css.core.db.models.base import BaseModel
from css.core.db.fields import DescriptionField, UrlField, VersionField


class MarketplaceAsset(BaseModel):
    """Base model for all marketplace assets (MCPs, skills, agents, plugins, workflows, prompts)."""

    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    asset_type = fields.CharField(
        max_length=32,
        db_index=True,
        description="Type: mcp, skill, agent, prompt, plugin, workflow"
    )
    description = DescriptionField(default="")
    version = VersionField(max_length=32, default="0.1.0", db_index=True)
    status = fields.CharField(
        max_length=32,
        default="available",
        db_index=True,
        description="Status: available, installed, disabled"
    )
    metadata = fields.JSONField(default=dict, description="Extended metadata (tags, category, etc.)")
    install_count = fields.IntField(default=0)
    last_updated = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "marketplace_assets"
        ordering = ["asset_type", "name"]
        indexes = [("asset_type", "status"), ("asset_type", "version")]


class MarketplaceMCP(BaseModel):
    """Model for externalized MCP packages."""

    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    description = DescriptionField(default="")
    version = VersionField(max_length=32, default="0.1.0", db_index=True)
    status = fields.CharField(
        max_length=32,
        default="available",
        db_index=True,
        description="Status: available, installed, disabled"
    )
    tools_count = fields.IntField(default=0)
    size_mb = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    repository_url = UrlField(max_length=512, default="", description="Git repository URL")
    documentation_url = UrlField(max_length=512, default="", description="Documentation link")
    category = fields.CharField(max_length=128, default="core", db_index=True)
    tags = fields.JSONField(default=list, description="Tags for discovery (e.g. forensics, network)")
    metadata = fields.JSONField(default=dict, description="MCP-specific metadata")
    install_count = fields.IntField(default=0)
    last_updated = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "marketplace_mcps"
        ordering = ["category", "name"]
        indexes = [("category", "status"), ("category", "version")]


class MarketplaceSkill(BaseModel):
    """Model for marketplace skills."""

    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    description = DescriptionField(default="")
    version = VersionField(max_length=32, default="0.1.0", db_index=True)
    status = fields.CharField(
        max_length=32,
        default="available",
        db_index=True,
        description="Status: available, installed, disabled"
    )
    category = fields.CharField(max_length=128, default="general", db_index=True)
    tags = fields.JSONField(default=list, description="Tags for discovery")
    metadata = fields.JSONField(default=dict, description="Skill-specific metadata")
    install_count = fields.IntField(default=0)
    last_updated = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "marketplace_skills"
        table_description = "Marketplace skills"
        ordering = ["category", "name"]
        indexes = [("category", "status"), ("category", "version")]


class MarketplaceAgent(BaseModel):
    """Model for marketplace agents."""

    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    description = DescriptionField(default="")
    version = VersionField(max_length=32, default="0.1.0", db_index=True)
    status = fields.CharField(
        max_length=32,
        default="available",
        db_index=True,
        description="Status: available, installed, disabled"
    )
    category = fields.CharField(max_length=128, default="general", db_index=True)
    model = fields.CharField(max_length=64, default="sonnet", description="LLM model to use")
    max_turns = fields.IntField(default=20, description="Max conversation turns")
    tags = fields.JSONField(default=list, description="Tags for discovery")
    metadata = fields.JSONField(default=dict, description="Agent-specific metadata")
    install_count = fields.IntField(default=0)
    last_updated = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "marketplace_agents"
        ordering = ["category", "name"]
        indexes = [("category", "status"), ("category", "model")]


class MarketplacePlugin(BaseModel):
    """Model for marketplace browser plugins."""

    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    description = DescriptionField(default="")
    version = VersionField(max_length=32, default="0.1.0", db_index=True)
    status = fields.CharField(
        max_length=32,
        default="available",
        db_index=True,
        description="Status: available, installed, disabled"
    )
    browser_types = fields.JSONField(default=list, description="Supported browsers: chrome, firefox, safari, edge")
    category = fields.CharField(max_length=128, default="general", db_index=True)
    tags = fields.JSONField(default=list, description="Tags for discovery")
    metadata = fields.JSONField(default=dict, description="Plugin-specific metadata")
    install_count = fields.IntField(default=0)
    last_updated = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "marketplace_plugins"
        ordering = ["category", "name"]
        indexes = [("category", "status"), ("category", "browser_types")]


class MarketplaceWorkflow(BaseModel):
    """Model for marketplace workflows."""

    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=256, db_index=True, unique=True)
    description = DescriptionField(default="")
    version = VersionField(max_length=32, default="0.1.0", db_index=True)
    status = fields.CharField(
        max_length=32,
        default="available",
        db_index=True,
        description="Status: available, installed, disabled"
    )
    category = fields.CharField(max_length=128, default="general", db_index=True)
    tags = fields.JSONField(default=list, description="Tags for discovery")
    steps = fields.JSONField(default=list, description="Workflow steps/tasks")
    metadata = fields.JSONField(default=dict, description="Workflow-specific metadata")
    install_count = fields.IntField(default=0)
    last_updated = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "marketplace_workflows"
        ordering = ["category", "name"]
        indexes = [("category", "status"), ("category", "version")]
