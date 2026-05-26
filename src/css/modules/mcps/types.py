"""Runtime value types for MCP registry and client operations."""

import msgspec

from .enums import McpServerStatus, McpTransport


class McpServerConfig(msgspec.Struct, kw_only=True):
    """Normalized MCP server runtime configuration."""

    server_id: str
    name: str
    transport: McpTransport = McpTransport.PYTHON_DIRECT
    command: str | None = None
    env: dict[str, str] = msgspec.field(default_factory=dict)
    url: str | None = None
    module_path: str | None = None
    auto_connect: bool = False
    enabled: bool = True
    status: McpServerStatus = McpServerStatus.DISCONNECTED
    timeout_seconds: int = 30
    metadata: dict[str, object] = msgspec.field(default_factory=dict)


class McpCallResult(msgspec.Struct, kw_only=True):
    """Canonical result payload for MCP tool invocations."""

    server_id: str
    tool_name: str
    content: str
    is_error: bool = False
