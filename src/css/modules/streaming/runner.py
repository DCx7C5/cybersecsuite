"""agents.runner — QueryExecutor: multi-turn ClaudeSDKClient wrapper.

Provides a high-level interface for running forensic agents queries
with session persistence, mode switching, and streaming support.

Enhanced to support TeamLeader delegation (Team-based orchestration).
"""


from legacy.logger import getLogger
from collections.abc import AsyncGenerator
from typing import Any, Optional
import uuid
from datetime import datetime

logger = getLogger("agents.runner")

_MODE_PREFIXES: dict[str, str] = {
    "blue":   "",
    "red":    "[MODE: RED] ",
    "purple": "[MODE: PURPLE] ",
}


class QueryExecutor:
    """Multi-turn agents runner backed by ClaudeSDKClient or TeamLeader.

    Usage (individual agent):
        runner = AgentRunner(agent_name="cybersec-analyst", mode="blue")
        result = await runner.query("Analyse CVE-2024-1234")
        session_id = runner.session_id  # resume later

    Or with client pool:
        from css.core.orchestration.client_pool import get_pool
        pool = get_pool()
        runner = AgentRunner(agent_name="cybersec-agents", pool=pool)

    Or with Team (Team-based delegation):
        runner = AgentRunner(agent_name="cybersec-team", team_id=1, orchestrator_id="orch-001")
        result = await runner.query("Analyse CVE-2024-1234")  # delegates to TeamLeader
    """

    def __init__(
        self,
        agent_name: str = "cybersec-agents",
        session_id: str | None = None,
        mode: str = "blue",
        extra_tools: list[str] | None = None,
        pool: Any | None = None,
        team_id: Optional[int] = None,
        orchestrator_id: Optional[str] = None,
    ) -> None:
        self.agent_name = agent_name
        self.session_id = session_id
        self.mode = mode
        self.extra_tools = extra_tools or []
        self.pool = pool
        self._client: Any | None = None  # ClaudeSDKClient
        self.team_id = team_id
        self.orchestrator_id = orchestrator_id
        self._team_leader: Any | None = None  # TeamLeader (lazy-loaded)
        
        # Validate team context (B10)
        self._validate_team_context()
    
    def _validate_team_context(self) -> None:
        """Validate that team_id and orchestrator_id are both provided or both None."""
        has_team = self.team_id is not None
        has_orch = self.orchestrator_id is not None
        
        if has_team != has_orch:
            raise ValueError(
                "Both team_id and orchestrator_id must be provided together "
                f"(team_id={self.team_id}, orchestrator_id={self.orchestrator_id})"
            )

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _get_prefix(self) -> str:
        return _MODE_PREFIXES.get(self.mode, f"[MODE: {self.mode.upper()}] ")

    async def _get_team_leader(self) -> Any:
        """Lazily initialize TeamLeader (for Team-based delegation)."""
        if self.team_id is None or self.orchestrator_id is None:
            return None
        
        if self._team_leader is None:
            from css.modules.orchestration import TeamLeader
            self._team_leader = TeamLeader(self.team_id, self.orchestrator_id)
            await self._team_leader.initialize()
        
        return self._team_leader

    async def _get_client(self) -> Any:
        """Lazily initialise ClaudeSDKClient (reuse across turns) or get from pool."""
        # Use pool if provided
        if self.pool is not None:
            return await self.pool.acquire(self.session_id)

        if self._client is None:
            from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

            try:
                from a2a.agent_sdk import build_agent_options
                options = build_agent_options(extra_tools=self.extra_tools)
            except ImportError:
                options = ClaudeAgentOptions()

            if self.session_id:
                options.resume = self.session_id
            self._client = ClaudeSDKClient(options=options)
        return self._client

    # ── Public API ───────────────────────────────────────────────────────────

    async def query(self, prompt: str) -> str:
        """Run a single-turn query; returns the result text.
        
        If team_id + orchestrator_id provided: delegates to TeamLeader
        Otherwise: uses ClaudeSDKClient directly
        """
        from css.core.types import Query
        
        # Try Team-based delegation first
        team_leader = await self._get_team_leader()
        if team_leader is not None:
            # Create typed Query object (B5)
            query_obj = Query(
                id=str(uuid.uuid4()),
                prompt=prompt,
                mode=self.mode,
                agent_name=self.agent_name,
                metadata={"created_at": datetime.now().isoformat()},
            )
            
            # Delegate to TeamLeader with typed Query
            result = await team_leader.delegate(query_obj)
            return result.get("result", "") if isinstance(result, dict) else str(result)
        
        # Fallback: direct ClaudeSDKClient
        from claude_agent_sdk import query, ResultMessage, SystemMessage, ClaudeAgentOptions

        try:
            from a2a.agent_sdk import build_agent_options
            options = build_agent_options(extra_tools=self.extra_tools)
        except ImportError:
            options = ClaudeAgentOptions()

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
        """Clean up the SDK client, release to pool, or shutdown TeamLeader."""
        # Close TeamLeader if active
        if self._team_leader is not None:
            await self._team_leader.shutdown()
            self._team_leader = None
        
        # Close SDK client
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
        if self.team_id:
            return (
                f"AgentRunner(agent={self.agent_name!r}, "
                f"team_id={self.team_id}, orchestrator={self.orchestrator_id!r})"
            )
        return (
            f"AgentRunner(agent={self.agent_name!r}, "
            f"mode={self.mode!r}, session={self.session_id!r})"
        )
