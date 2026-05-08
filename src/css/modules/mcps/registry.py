"""MCP Runtime Registry — multiserver management with AsyncSafeSingletonMeta."""

from typing import TYPE_CHECKING

from css.core.types.meta import AsyncSafeSingletonMeta

if TYPE_CHECKING:
    from .types import McpServerConfig, McpCallResult
    from .enums import McpTransportType


class McpRuntimeRegistry(metaclass=AsyncSafeSingletonMeta):
    """Multi-server MCP runtime registry (singleton).

    Uses AsyncSafeSingletonMeta for async-safe singleton pattern.
    Manages connections to multiple MCP servers with different transports.
    """

    _initialized: bool = False

    def __init__(self) -> None:
        """Initialize the registry (runs setup only once)."""
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        self._servers: dict[str, McpServerConfig] = {}
        self._tool_to_server: dict[str, str] = {}  # tool_id → server_id
        self._connections: dict[str, object] = {}  # server_id → Client

    async def register(
        self,
        server_id: str,
        config: "McpServerConfig",
    ) -> None:
        """Register a MCP server configuration."""
        self._servers[server_id] = config
        # Persist to DB if models are available
        try:
            from .models import McpServerConfigRecord

            await McpServerConfigRecord.update_or_create(
                server_id=server_id,
                defaults=config.__dict__,
            )
        except ImportError:
            pass  # Models not yet created

    async def connect(self, server_id: str) -> None:
        """Connect to a registered MCP server using its transport type."""
        from fastmcp import Client
        from fastmcp.client.transports import (
            UvStdioTransport,
            SSETransport,
            StreamableHttpTransport,
        )

        config = self._servers[server_id]
        transport = config.transport
        transport_value = getattr(transport, "value", transport)

        if transport_value == "PYTHON_DIRECT":
            module, attr = config.module_path.rsplit(":", 1)
            from importlib import import_module

            server = getattr(import_module(module), attr)()
            client = await Client(server)  # In-process, zero HTTP
        elif transport_value == "STDIO":
            client = await Client(
                UvStdioTransport(config.command, env=config.env)
            )
        elif transport_value == "STREAMABLE_HTTP":
            url = config.url or ""
            client = await Client(StreamableHttpTransport(url))
        else:  # SSE
            url = config.url or ""
            client = await Client(SSETransport(url))

        self._connections[server_id] = client

    async def disconnect(self, server_id: str) -> None:
        """Disconnect from an MCP server."""
        if server_id in self._connections:
            client = self._connections[server_id]
            if hasattr(client, "close"):
                await client.close()
            del self._connections[server_id]

    async def call_tool(
        self,
        tool_id: str,
        args: dict,
    ) -> "McpCallResult":
        """Call a tool on its registered MCP server."""
        from .types import McpCallResult

        server_id = self._tool_to_server.get(tool_id)
        if not server_id or server_id not in self._connections:
            raise RuntimeError(f"Server not connected for tool: {tool_id}")

        client = self._connections[server_id]
        result = await client.call_tool(tool_id, args)

        return McpCallResult(
            server_id=server_id,
            tool_name=tool_id,
            content=str(result) if result else "",
            is_error=bool(getattr(result, "is_error", False)),
        )

    async def list_tools(self, server_id: str) -> list[dict]:
        """List all tools available from a connected MCP server."""
        if server_id not in self._connections:
            raise RuntimeError(f"Server not connected: {server_id}")
        client = self._connections[server_id]
        tools = await client.list_tools()
        return [t.__dict__ for t in tools] if tools else []

    def register_tool_mapping(self, tool_id: str, server_id: str) -> None:
        """Register a tool_id → server_id mapping."""
        self._tool_to_server[tool_id] = server_id

    async def load_from_db(self) -> None:
        """Restore server configurations from DB on startup."""
        try:
            from .models import McpServerConfigRecord

            records = await McpServerConfigRecord.all()
            for rec in records:
                config = rec.to_schema()  # Returns McpServerConfig
                self._servers[rec.server_id] = config
        except (ImportError, RuntimeError):
            pass  # Models not yet created

    async def auto_connect(self) -> None:
        """Connect all servers with auto_connect=True."""
        for server_id, config in self._servers.items():
            if getattr(config, "auto_connect", False):
                try:
                    await self.connect(server_id)
                except Exception as e:
                    from css.core.logger import getLogger

                    logger = getLogger(__name__)
                    logger.warning(f"Failed to auto-connect to {server_id}: {e}")


def get_mcp_registry() -> McpRuntimeRegistry:
    """Return the global McpRuntimeRegistry singleton."""
    return McpRuntimeRegistry()


__all__ = ["McpRuntimeRegistry", "get_mcp_registry"]
