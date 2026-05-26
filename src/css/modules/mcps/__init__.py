"""MCP protocol layer.

Provides MCP server lifecycle management, runtime registry, and async client wrapper.

Exports:
- McpRuntimeRegistry: Multi-server connection registry
- McpClient: Async client wrapper for fastmcp transports
- endpoints.router: FastAPI router for lifecycle endpoints (start/stop/restart)
"""

from .client import McpClient
from .endpoints import router as lifecycle_router
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
    "lifecycle_router",
]
