"""
Tool registry — unified table for all tools across all sources.

Tables:
  tool_registry        — canonical tool catalog (mcp/sdk_builtin/sdk_beta/agent_sdk)
  tool_toggle_state    — per-scope on/off state (DB-backed, replaces JSON files)
  tool_toggle_registry — global exclusivity index (tool → active scope)
  account_tool_access  — which tools an account+tier can use
"""
from tortoise import fields
from tortoise.models import Model

from db.models.enums import ModelTier, ToolType, ToggleScopeType


class ToolRegistry(Model):
    """
    Unified catalog of every tool available in CyberSecSuite.

    Covers three tiers of tools:
    - Own MCP tools   : mcp_cybersec / mcp_dystopian (vault_scaffold, canvas_create, …)
    - Anthropic SDK   : sdk_builtin (computer_use_20250124, web_search_20250305, …)
                        sdk_beta    (memory_20250818, skills-2025-05-15, …)
    - Agent SDK tools : agent_sdk   (tools registered in agent YAML definitions)

    tool_name is the canonical unique key (snake_case, globally unique across all types).
    """

    id = fields.UUIDField(pk=True)

    # Identity
    tool_name = fields.CharField(max_length=128, unique=True)
    display_name = fields.CharField(max_length=255, default="")
    description = fields.TextField(default="")
    tool_type = fields.CharEnumField(ToolType)

    # MCP server name if tool_type is mcp_* (e.g. "cybersec", "dystopian")
    mcp_server = fields.CharField(max_length=64, null=True)

    # For sdk_builtin / sdk_beta: the exact string for the `type` field
    # e.g. "computer_use_20250124", "web_search_20250305", "memory_20250818"
    sdk_type_string = fields.CharField(max_length=128, null=True)

    # For sdk_beta: the beta header required to unlock it
    # e.g. "computer-use-2025-01-24", "memory-2025-08-18"
    required_beta = fields.CharField(max_length=128, null=True)

    # For agent_sdk: which agent definition file owns this tool
    agent_source = fields.CharField(max_length=255, null=True)

    # Input JSON schema (the 'input_schema' / 'parameters' dict)
    input_schema = fields.JSONField(default=dict)

    # Access control
    min_tier = fields.CharEnumField(ModelTier, default=ModelTier.FREE)

    # Provider restriction: null = works with any provider
    # Non-null = e.g. "anthropic" (computer_use only works on Anthropic)
    required_provider = fields.CharField(max_length=40, null=True)

    # Toggle default: tools are enabled by default unless explicitly disabled
    enabled_by_default = fields.BooleanField(default=True)
    deprecated = fields.BooleanField(default=False)
    deprecated_at = fields.DatetimeField(null=True)

    # Schema version / last sync
    version = fields.CharField(max_length=32, default="1")
    tags = fields.JSONField(default=list)           # e.g. ["forensics", "vault", "canvas"]

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tool_registry"
        ordering = ["tool_type", "tool_name"]

    def __str__(self) -> str:
        return f"Tool({self.tool_name} [{self.tool_type}])"


class ToolToggleState(Model):
    """
    Per-scope toggle state for a tool.

    A tool can have at most one toggle state per (tool, scope_type, scope_id).
    scope_id is null for GLOBAL, project name for PROJECT, session id for SESSION.

    The DB-backed version of what was previously stored in JSON files.
    """

    id = fields.UUIDField(pk=True)
    tool = fields.ForeignKeyField(
        "models.ToolRegistry", related_name="toggle_states", on_delete=fields.CASCADE
    )

    scope_type = fields.CharEnumField(ToggleScopeType)
    scope_id = fields.CharField(max_length=255, null=True)   # null → global

    enabled = fields.BooleanField()
    set_by = fields.CharField(max_length=128, null=True)     # agent name or "user"

    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tool_toggle_states"
        unique_together = (("tool", "scope_type", "scope_id"),)

    def __str__(self) -> str:
        sid = self.scope_id or "*"
        return f"Toggle({self.tool_id} @ {self.scope_type}/{sid} = {self.enabled})"


class ToolToggleRegistry(Model):
    """
    Exclusivity index — tracks which scope currently holds the *active* (enabled=True)
    toggle for each tool.

    Invariant: a tool can only be enabled=True in ONE scope at a time.
    When tool_toggle_set enables a tool at scope X, this row is updated and
    all other ToolToggleState rows for that tool are cleared.
    """

    tool = fields.OneToOneField(
        "models.ToolRegistry", related_name="active_toggle", on_delete=fields.CASCADE
    )

    active_scope_type = fields.CharEnumField(ToggleScopeType, null=True)
    active_scope_id = fields.CharField(max_length=255, null=True)

    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tool_toggle_registry"

    def __str__(self) -> str:
        if self.active_scope_type:
            return f"ToggleRegistry({self.tool_id} → {self.active_scope_type}/{self.active_scope_id or '*'})"
        return f"ToggleRegistry({self.tool_id} → inactive)"


class AccountToolAccess(Model):
    """
    Records which tools an API account can access, and under what conditions.

    Reflects the combination of: account tier + provider capabilities + beta enrollments.
    Used by routing logic to check "can account X call tool Y?".

    Populated by the tool_access_sync job that cross-references:
    - account.provider  → provider capabilities
    - account tier      → tool.min_tier
    - beta enrollments  → tool.required_beta
    """

    id = fields.UUIDField(pk=True)
    account = fields.ForeignKeyField(
        "models.ApiAccount", related_name="tool_access", on_delete=fields.CASCADE
    )
    tool = fields.ForeignKeyField(
        "models.ToolRegistry", related_name="account_access", on_delete=fields.CASCADE
    )

    accessible = fields.BooleanField(default=True)
    access_reason = fields.CharField(max_length=512, null=True)  # why accessible or not

    # Beta headers that need to be sent for this account+tool combo
    required_betas = fields.JSONField(default=list)

    # Effective tier for this account+tool (may differ from tool.min_tier if overridden)
    effective_tier = fields.CharEnumField(ModelTier, null=True)

    last_verified_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "account_tool_access"
        unique_together = (("account", "tool"),)

    def __str__(self) -> str:
        return f"AccountToolAccess({self.account_id} → {self.tool_id}: {self.accessible})"
