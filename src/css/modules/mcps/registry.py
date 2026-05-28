"""MCP runtime registry for multi-server connection and tool routing."""

from collections.abc import Callable
from typing import override

from css.core.logger import getLogger
from css.core.types.base_registry import BaseToggleRegistry

from .client import McpClient
from .enums import McpServerStatus
from .models import McpServerConfigRecord
from .types import McpCallResult, McpServerConfig

logger = getLogger(__name__)


class McpRuntimeRegistry(BaseToggleRegistry[McpServerConfig]):
    """Multi-server MCP runtime registry."""

    _initialized: bool = False

    def __init__(self) -> None:
        """Initialize the registry (runs setup only once)."""
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        self._servers: dict[str, McpServerConfig] = {}
        self._tool_to_server: dict[str, str] = {}  # tool_id → server_id
        self._connections: dict[str, McpClient] = {}  # server_id → async MCP client

    async def register(
        self,
        server_id: str,
        config: McpServerConfig,
    ) -> None:
        """Register a MCP server configuration in memory."""
        self._servers[server_id] = config

    async def connect(self, server_id: str) -> None:
        """Connect to a registered MCP server."""
        config = self._servers.get(server_id)
        if config is None:
            raise RuntimeError(f"MCP server config not registered: {server_id}")
        if server_id in self._connections:
            return

        config.status = McpServerStatus.CONNECTING
        client = McpClient(config)
        try:
            await client.connect()
        except Exception:
            config.status = McpServerStatus.ERROR
            raise
        config.status = McpServerStatus.CONNECTED
        self._connections[server_id] = client

    async def disconnect(self, server_id: str) -> None:
        """Disconnect from an MCP server."""
        client = self._connections.pop(server_id, None)
        if client is not None:
            await client.close()
        config = self._servers.get(server_id)
        if config is not None:
            config.status = McpServerStatus.DISCONNECTED

    async def call_tool(
        self,
        tool_id: str,
        args: dict[str, object],
    ) -> McpCallResult:
        """Call a tool on its registered MCP server."""
        server_id = self._tool_to_server.get(tool_id)
        if not server_id or server_id not in self._connections:
            raise RuntimeError(f"Server not connected for tool: {tool_id}")

        client = self._connections[server_id]
        result = await client.call_tool(tool_id, args)
        is_error = bool(
            getattr(result, "isError", False)
            or getattr(result, "is_error", False)
        )

        return McpCallResult(
            server_id=server_id,
            tool_name=tool_id,
            content=str(result) if result else "",
            is_error=is_error,
        )

    async def list_tools(self, server_id: str) -> list[dict[str, object]]:
        """List all tools available from a connected MCP server."""
        if server_id not in self._connections:
            raise RuntimeError(f"Server not connected: {server_id}")
        tools = await self._connections[server_id].list_tools()
        return [_tool_to_dict(tool) for tool in tools]

    def register_tool_mapping(self, tool_id: str, server_id: str) -> None:
        """Register a tool_id → server_id mapping."""
        self._tool_to_server[tool_id] = server_id

    @override
    async def get(self, identifier: str) -> McpServerConfig | None:
        """Return a registered MCP server config by server ID."""
        return self._servers.get(identifier)

    @override
    async def list(
        self,
        predicate: Callable[[McpServerConfig], bool] | None = None,
    ) -> list[McpServerConfig]:
        """List registered MCP server configs."""
        configs = list(self._servers.values())
        if predicate is None:
            return configs
        return [config for config in configs if predicate(config)]

    @override
    async def invalidate(self, identifier: str | None = None) -> None:
        """Invalidate one server runtime entry or clear all runtime entries."""
        if identifier is None:
            for server_id in list(self._connections):
                await self.disconnect(server_id)
            self._servers.clear()
            self._tool_to_server.clear()
            return

        await self.disconnect(identifier)
        self._servers.pop(identifier, None)
        self._tool_to_server = {
            tool_id: server_id
            for tool_id, server_id in self._tool_to_server.items()
            if server_id != identifier
        }

    @override
    async def reload(self) -> None:
        """Reload MCP server configurations from persisted DB state."""
        await self.invalidate()
        await self.load_from_db()

    @override
    async def enable(self, identifier: str) -> None:
        """Enable a registered server config by ID."""
        config = self._servers.get(identifier)
        if config is None:
            raise RuntimeError(f"MCP server config not found: {identifier}")
        config.enabled = True

    @override
    async def disable(self, identifier: str) -> None:
        """Disable a registered server config by ID and disconnect it."""
        config = self._servers.get(identifier)
        if config is None:
            raise RuntimeError(f"MCP server config not found: {identifier}")
        config.enabled = False
        await self.disconnect(identifier)

    @override
    async def is_enabled(self, identifier: str) -> bool:
        """Check whether a server config is enabled."""
        config = self._servers.get(identifier)
        if config is None:
            raise RuntimeError(f"MCP server config not found: {identifier}")
        return bool(config.enabled)

    async def load_from_db(self) -> None:
        """Restore server configurations from DB on startup."""
        records = await McpServerConfigRecord.all()
        for rec in records:
            self._servers[rec.server_id] = rec.to_schema()

    async def auto_connect(self) -> None:
        """Connect all servers with auto_connect=True."""
        for server_id, config in self._servers.items():
            if config.auto_connect and config.enabled:
                try:
                    await self.connect(server_id)
                except Exception as e:
                    logger.warning(f"Failed to auto-connect to {server_id}: {e}")

    @property
    def connections(self):
        return self._connections

    @property
    def servers(self):
        return self._servers


def get_mcp_registry() -> McpRuntimeRegistry:
    """Return the global McpRuntimeRegistry singleton."""
    return McpRuntimeRegistry()


def _tool_to_dict(tool: object) -> dict[str, object]:
    """Normalize a fastmcp tool object into a JSON-safe dict shape."""
    if isinstance(tool, dict):
        return dict(tool)
    if hasattr(tool, "__dict__"):
        return dict(vars(tool))
    return {"name": str(tool)}


__all__ = ["McpRuntimeRegistry", "get_mcp_registry"]
