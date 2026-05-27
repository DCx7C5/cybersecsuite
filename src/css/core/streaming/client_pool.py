"""Client pool for SDK agent client instances — concurrent session management."""

from css.core.logger import getLogger
import asyncio
from typing import Protocol, runtime_checkable

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from css.core.types.base_meta import singleton

logger = getLogger("agents.client_pool")


@runtime_checkable
class SDKClientProtocol(Protocol):
    """Structural protocol for any SDK client managed by the pool."""

    async def disconnect(self) -> None: ...


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
        self._checked_out: list[SDKClientProtocol] = []
        self._condition = asyncio.Condition()

    async def _create_client(self, session_id: str | None = None) -> SDKClientProtocol:
        """Create a new ClaudeSDKClient instance."""
        options = ClaudeAgentOptions()

        if session_id:
            options.resume = session_id
        return ClaudeSDKClient(options=options)

    async def acquire(self, session_id: str | None = None) -> SDKClientProtocol:
        """Acquire a client from the pool."""
        async with self._condition:
            while True:
                if session_id and session_id in self._pool:
                    logger.debug("reusing existing client for session %s", session_id)
                    return self._pool[session_id]

                if self._available:
                    client = self._available.pop()
                    logger.debug("reused available client for session %s", session_id)
                    break

                current_count = len(self._checked_out) + len(self._available)
                if current_count < self._max_size:
                    client = await self._create_client(session_id)
                    logger.debug("created new client for session %s (pool size: %s)", session_id, current_count + 1)
                    break

                logger.warning("pool exhausted, waiting for available client")
                await self._condition.wait()

            self._checked_out.append(client)
            if session_id:
                self._pool[session_id] = client
            return client

    async def release(self, client: SDKClientProtocol, session_id: str | None = None) -> None:
        """Release a checked-out client back to the pool."""
        async with self._condition:
            checked_out_index = next(
                (index for index, candidate in enumerate(self._checked_out) if candidate is client),
                None,
            )
            if checked_out_index is None:
                logger.warning("ignoring release of client that is not checked out")
                return

            self._checked_out.pop(checked_out_index)
            for mapped_session, mapped_client in list(self._pool.items()):
                if mapped_client is client:
                    del self._pool[mapped_session]

            self._available.append(client)
            self._condition.notify(1)
            logger.debug("released client to pool for session %s", session_id)

    def get(self, session_id: str) -> SDKClientProtocol | None:
        """Get client by session_id without acquiring."""
        return self._pool.get(session_id)

    def size(self) -> tuple[int, int, int]:
        """Return (checked out, available, max_size)."""
        return len(self._checked_out), len(self._available), self._max_size

    async def close(self) -> None:
        """Close all clients in pool."""
        async with self._condition:
            clients = [*self._checked_out, *self._available]
            self._pool.clear()
            self._checked_out.clear()
            self._available.clear()
            self._condition.notify_all()

        closed: list[SDKClientProtocol] = []
        for client in clients:
            if any(candidate is client for candidate in closed):
                continue
            closed.append(client)
            try:
                await client.disconnect()
            except Exception:
                pass
        logger.info("client pool closed")


@singleton
class _PoolSingleton:
    """Singleton wrapper holding the global ClientPool instance."""

    def __init__(self) -> None:
        self.pool = ClientPool(max_size=6, default_size=4)


def get_pool() -> ClientPool:
    """Get the global ClientPool singleton."""
    return _PoolSingleton().pool
