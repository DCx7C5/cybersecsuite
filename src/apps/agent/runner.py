"""agent.runner — AgentRunner: multi-turn ClaudeSDKClient wrapper.

Provides a high-level interface for running forensic agent queries
with session persistence, mode switching, and streaming support.
"""


from agent import getLogger
from collections.abc import AsyncGenerator
from typing import Any

logger = getLogger("agent.runner")

_MODE_PREFIXES: dict[str, str] = {
    "blue":   "",
    "red":    "[MODE: RED] ",
    "purple": "[MODE: PURPLE] ",
}


class AgentRunner:
    """Multi-turn agent runner backed by ClaudeSDKClient.

    Usage:
        runner = AgentRunner(agent_name="cybersec-analyst", mode="blue")
        result = await runner.query("Analyse CVE-2024-1234")
        session_id = runner.session_id  # resume later

    Or with pool:
        from agent import get_pool
        pool = get_pool()
        runner = AgentRunner(agent_name="cybersec-agent", pool=pool)
    """

    def __init__(
        self,
        agent_name: str = "cybersec-agent",
        session_id: str | None = None,
        mode: str = "blue",
        extra_tools: list[str] | None = None,
        pool: Any | None = None,
    ) -> None:
        self.agent_name = agent_name
        self.session_id = session_id
        self.mode = mode
        self.extra_tools = extra_tools or []
        self.pool = pool
        self._client: Any | None = None  # ClaudeSDKClient

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _get_prefix(self) -> str:
        return _MODE_PREFIXES.get(self.mode, f"[MODE: {self.mode.upper()}] ")

    async def _get_client(self) -> Any:
        """Lazily initialise ClaudeSDKClient (reuse across turns) or get from pool."""
        # Use pool if provided
        if self.pool is not None:
            return await self.pool.acquire(self.session_id)

        if self._client is None:
            from claude_agent_sdk import ClaudeSDKClient
            from a2a.agent_sdk import build_agent_options
            options = build_agent_options(extra_tools=self.extra_tools)
            if self.session_id:
                options.resume = self.session_id
            self._client = ClaudeSDKClient(options=options)
        return self._client

    # ── Public API ───────────────────────────────────────────────────────────

    async def query(self, prompt: str) -> str:
        """Run a single-turn query; returns the result text."""
        from claude_agent_sdk import query, ResultMessage, SystemMessage
        from a2a.agent_sdk import build_agent_options

        options = build_agent_options(extra_tools=self.extra_tools)
        if self.session_id:
            options.resume = self.session_id

        full_prompt = f"{self._get_prefix()}{prompt}"
        result_text = ""

        async for message in query(prompt=full_prompt, options=options):
            if isinstance(message, SystemMessage) and message.subtype == "init":
                self.session_id = message.data.get("session_id") or self.session_id
            elif isinstance(message, ResultMessage) and message.subtype == "success":
                result_text = message.result or ""

        return result_text

    async def stream(self, prompt: str) -> AsyncGenerator[dict[str, Any], None]:
        """Stream a query, yielding SSE-ready dicts."""
        from agent.streaming import stream_query
        async for chunk in stream_query(
            prompt=prompt,
            agent_name=self.agent_name,
            mode=self.mode,
            session_id=self.session_id,
            extra_tools=self.extra_tools,
        ):
            if chunk.get("type") == "result":
                self.session_id = chunk.get("session_id") or self.session_id
            yield chunk

    async def close(self) -> None:
        """Clean up the SDK client or release to pool."""
        if self.pool is not None and self._client is not None:
            await self.pool.release(self._client, self.session_id)
            self._client = None
        elif self._client is not None:
            try:
                await self._client.close()
            except Exception:
                pass
            self._client = None

    def __repr__(self) -> str:
        return (
            f"AgentRunner(agent={self.agent_name!r}, "
            f"mode={self.mode!r}, session={self.session_id!r})"
        )
