"""MCP protocol layer.

The package is still scaffold-level. Export only the runtime registry until the
remaining Phase 22 types, enums, and exceptions land.
"""

from .client import McpClient
from .enums import McpServerStatus, McpTransport
from .registry import McpRuntimeRegistry, get_mcp_registry
from .types import McpCallResult, McpServerConfig

from css.core.logger import getLogger

logger = getLogger(__name__)

__all__ = [
    "McpRuntimeRegistry",
    "get_mcp_registry",
    "McpClient",
    "McpTransport",
    "McpServerStatus",
    "McpServerConfig",
    "McpCallResult",
]
