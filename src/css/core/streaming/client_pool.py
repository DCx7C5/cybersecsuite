"""Client pool for SDK agent client instances — concurrent session management."""

from css.core.logger import getLogger
import asyncio
from typing import Protocol, runtime_checkable

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from css.core.types.meta import singleton

logger = getLogger("agents.client_pool")


@runtime_checkable
class SDKClientProtocol(Protocol):
    """Structural protocol for any SDK client managed by the pool."""

    async def close(self) -> None: ...


class ClientPool:
    """Pool of SDK client instances for concurrent sessions.

    Usage:
        pool = ClientPool(max_size=6, default_size=4)
        client = await pool.acquire("session-123")
        # ... use client ...
        await pool.release(client)
    """

    def __init__(self, max_size: int = 6, default_size: int = 4) -> None:
        self._max_size = max_size
        self._default_size = default_size
        self._pool: dict[str, SDKClientProtocol] = {}
        self._available: list[SDKClientProtocol] = []
        self._lock = asyncio.Lock()

    async def _create_client(self, session_id: str | None = None) -> SDKClientProtocol:
        """Create a new ClaudeSDKClient instance."""
        options = ClaudeAgentOptions()

        if session_id:
            options.resume = session_id
        return ClaudeSDKClient(options=options)

    async def acquire(self, session_id: str | None = None) -> SDKClientProtocol:
        """Acquire a client from the pool."""
        async with self._lock:
            if session_id and session_id in self._pool:
                logger.debug("reusing existing client for session %s", session_id)
                return self._pool[session_id]

            if self._available:
                client = self._available.pop()
                if session_id:
                    self._pool[session_id] = client
                logger.debug("reused available client for session %s", session_id)
                return client

            current_count = len(self._pool) + len(self._available)
            if current_count < self._max_size:
                client = await self._create_client(session_id)
                if session_id:
                    self._pool[session_id] = client
                logger.debug("created new client for session %s (pool size: %s)", session_id, current_count + 1)
                return client

            logger.warning("pool exhausted, waiting for available client")
            while not self._available:
                await asyncio.sleep(0.1)
            return await self.acquire(session_id)

    async def release(self, client: SDKClientProtocol, session_id: str | None = None) -> None:
        """Release a client back to the pool."""
        async with self._lock:
            if session_id and session_id in self._pool:
                del self._pool[session_id]
            if len(self._pool) + len(self._available) < self._max_size:
                self._available.append(client)
                logger.debug("released client to pool")
            else:
                try:
                    await client.close()
                except Exception:
                    pass
                logger.debug("closed excess client")

    def get(self, session_id: str) -> SDKClientProtocol | None:
        """Get client by session_id without acquiring."""
        return self._pool.get(session_id)

    def size(self) -> tuple[int, int, int]:
        """Return (active, available, max_size)."""
        return len(self._pool), len(self._available), self._max_size

    async def close(self) -> None:
        """Close all clients in pool."""
        async with self._lock:
            for client in self._pool.values():
                try:
                    await client.close()
                except Exception:
                    pass
            for client in self._available:
                try:
                    await client.close()
                except Exception:
                    pass
            self._pool.clear()
            self._available.clear()
            logger.info("client pool closed")


@singleton
class _PoolSingleton:
    """Singleton wrapper holding the global ClientPool instance."""

    def __init__(self) -> None:
        self.pool = ClientPool(max_size=6, default_size=4)


def get_pool() -> ClientPool:
    """Get the global ClientPool singleton."""
    return _PoolSingleton().pool
