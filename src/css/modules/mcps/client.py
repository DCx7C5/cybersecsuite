"""Async MCP client wrapper around ``fastmcp.Client`` transports."""

from importlib import import_module
import inspect
from typing import Any, cast

from .enums import McpTransport
from .types import McpServerConfig


class McpClient:
    """Transport-aware async MCP client lifecycle wrapper."""

    def __init__(self, config: McpServerConfig) -> None:
        self._config = config
        self._client: Any | None = None

    @property
    def connected(self) -> bool:
        """Whether an underlying client instance is currently available."""
        return self._client is not None

    async def connect(self) -> None:
        """Construct and initialize the underlying fastmcp client."""
        if self._client is not None:
            return

        client = self._build_client()

        connect_method = getattr(client, "connect", None)
        if callable(connect_method):
            await _resolve_maybe_awaitable(connect_method())
        elif hasattr(client, "__aenter__"):
            entered = await _resolve_maybe_awaitable(client.__aenter__())
            if entered is not None:
                client = entered

        self._client = client

    async def close(self) -> None:
        """Close/dispose the underlying fastmcp client."""
        if self._client is None:
            return

        client = self._client
        close_method = getattr(client, "close", None)
        if callable(close_method):
            await _resolve_maybe_awaitable(close_method())
        elif hasattr(client, "__aexit__"):
            await _resolve_maybe_awaitable(client.__aexit__(None, None, None))

        self._client = None

    async def call_tool(self, tool_name: str, args: dict[str, object]) -> object:
        """Invoke a tool on the connected MCP server."""
        client = await self._require_client()
        return await _resolve_maybe_awaitable(client.call_tool(tool_name, args))

    async def list_tools(self) -> list[object]:
        """List tools exposed by the connected MCP server."""
        client = await self._require_client()
        tools = await _resolve_maybe_awaitable(client.list_tools())
        if isinstance(tools, list):
            return tools
        return []

    async def _require_client(self) -> Any:
        if self._client is None:
            await self.connect()
        if self._client is None:
            raise RuntimeError(f"MCP client failed to initialize for server: {self._config.server_id}")
        return self._client

    def _build_client(self) -> Any:
        try:
            from fastmcp import Client
            from fastmcp.client.transports import (
                FastMCPTransport,
                SSETransport,
                StreamableHttpTransport,
                UvStdioTransport,
            )
        except ImportError as exc:
            raise RuntimeError(
                "fastmcp is required for MCP runtime connections. Install project dependencies first."
            ) from exc

        transport = self._config.transport
        if transport == McpTransport.PYTHON_DIRECT:
            if not self._config.module_path:
                raise ValueError(f"module_path is required for PYTHON_DIRECT ({self._config.server_id})")
            try:
                module, attr = self._config.module_path.rsplit(":", 1)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid module_path format for {self._config.server_id}: {self._config.module_path}"
                ) from exc

            module_obj = import_module(module)
            if not hasattr(module_obj, attr):
                raise ValueError(
                    f"module_path target missing for {self._config.server_id}: {self._config.module_path}"
                )
            server_factory = getattr(module_obj, attr)
            if not callable(server_factory):
                raise ValueError(
                    f"module_path target is not callable for {self._config.server_id}: {self._config.module_path}"
                )
            server = cast(Any, server_factory())
            return Client(FastMCPTransport(server))

        if transport == McpTransport.STDIO:
            if not self._config.command:
                raise ValueError(f"command is required for STDIO ({self._config.server_id})")
            return Client(UvStdioTransport(self._config.command, env_vars=self._config.env))

        if transport == McpTransport.STREAMABLE_HTTP:
            if not self._config.url:
                raise ValueError(f"url is required for STREAMABLE_HTTP ({self._config.server_id})")
            return Client(StreamableHttpTransport(self._config.url))

        if not self._config.url:
            raise ValueError(f"url is required for SSE ({self._config.server_id})")
        return Client(SSETransport(self._config.url))


async def _resolve_maybe_awaitable(value: object) -> object:
    """Await value if it is awaitable, otherwise return as-is."""
    if inspect.isawaitable(value):
        return await value
    return value
