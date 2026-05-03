from enum import Enum


class ToolStatus(str, Enum):
    """Status of a tool."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"


class ToolType(str, Enum):
    """Type of tool."""

    BUILTIN = "builtin"
    CUSTOM = "custom"
    EXTERNAL = "external"
    MCP = "mcp"
