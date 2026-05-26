"""ORM models for persisted MCP runtime configuration."""

from tortoise import fields
from tortoise.fields import CharEnumField

from css.core.db.models.base import BaseModel
from css.core.db.models.mixins import TimestampMixin

from .enums import McpServerStatus, McpTransport
from .types import McpServerConfig


class McpServerConfigRecord(BaseModel, TimestampMixin):
    """Persisted MCP server configuration for startup restore."""

    server_id = fields.CharField(max_length=128, unique=True, db_index=True)
    name = fields.CharField(max_length=255)
    transport = CharEnumField(McpTransport, default=McpTransport.PYTHON_DIRECT)
    command = fields.CharField(max_length=512, null=True)
    url = fields.CharField(max_length=512, null=True)
    module_path = fields.CharField(max_length=512, null=True)
    env = fields.JSONField(default=dict)  # type: ignore[var-annotated]
    auto_connect = fields.BooleanField(default=False)
    enabled = fields.BooleanField(default=True)
    status = CharEnumField(McpServerStatus, default=McpServerStatus.DISCONNECTED)
    timeout_seconds = fields.IntField(default=30)
    metadata = fields.JSONField(default=dict)  # type: ignore[var-annotated]

    def to_schema(self) -> McpServerConfig:
        """Convert persisted ORM row to runtime MCP server config."""

        return McpServerConfig(
            server_id=self.server_id,
            name=self.name,
            transport=self.transport,
            command=self.command,
            env=self.env or {},
            url=self.url,
            module_path=self.module_path,
            auto_connect=self.auto_connect,
            enabled=self.enabled,
            status=self.status,
            timeout_seconds=self.timeout_seconds,
            metadata=self.metadata or {},
        )

    @classmethod
    def from_schema(cls, config: McpServerConfig) -> "McpServerConfigRecord":
        """Build a persisted config row from runtime schema."""

        return cls(
            server_id=config.server_id,
            name=config.name,
            transport=config.transport,
            command=config.command,
            url=config.url,
            module_path=config.module_path,
            env=config.env,
            auto_connect=config.auto_connect,
            enabled=config.enabled,
            status=config.status,
            timeout_seconds=config.timeout_seconds,
            metadata=config.metadata,
        )

    class Meta(BaseModel.Meta, TimestampMixin.Meta):
        table = "mcp_server_config"
        ordering = ["server_id"]
