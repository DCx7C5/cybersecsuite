"""Enumeration types for MCP runtime configuration."""

from enum import Enum


class McpTransport(str, Enum):
    """Supported MCP transport mechanisms."""

    PYTHON_DIRECT = "PYTHON_DIRECT"
    STDIO = "STDIO"
    SSE = "SSE"
    STREAMABLE_HTTP = "STREAMABLE_HTTP"


class McpServerStatus(str, Enum):
    """Runtime connection state for a configured MCP server."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
