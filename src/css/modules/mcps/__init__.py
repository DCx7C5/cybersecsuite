"""MCP protocol layer.

The package is still scaffold-level. Export only the runtime registry until the
remaining Phase 22 types, enums, and exceptions land.
"""

from css.core.logger import getLogger

logger = getLogger(__name__)

from .registry import McpRuntimeRegistry, get_mcp_registry

__all__ = [
    "McpRuntimeRegistry",
    "get_mcp_registry",
]
