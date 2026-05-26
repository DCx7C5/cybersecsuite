"""agents.runner — QueryExecutor: provider-agnostic agent runner.

Provides a high-level interface for running agents queries
with session persistence, mode switching, and streaming support.

Uses AgentExecutor → ProviderRegistry → HttpProviderAdapter.
TeamLeader delegation when team_id + orchestrator_id are set.
"""

from css.core.logger import getLogger
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING
import uuid
from datetime import datetime

from css.core.streaming.client_pool import ClientPool

if TYPE_CHECKING:
    from css.modules.agents.base import AgentExecutor
    from css.modules.teams.orchestrator import TeamLeader


logger = getLogger("agents.runner")

_MODE_PREFIXES: dict[str, str] = {
    "blue":   "",
    "red":    "[MODE: RED] ",
    "purple": "[MODE: PURPLE] ",
}


class QueryExecutor:
    """Multi-turn agent runner backed by AgentExecutor + TeamLeader.
    
    Provider-agnostic: uses AgentExecutor → HttpProviderAdapter.
    
    Usage (individual agent):
        runner = QueryExecutor(agent_name="cybersec-analyst", mode="blue")
        result = await runner.query("Analyse CVE-2024-1234")
        session_id = runner.session_id  # resume later
    
    Or with client pool:
        from css.core.streaming.client_pool import get_pool
        pool = get_pool()
        runner = QueryExecutor(agent_name="cybersec-agent", pool=pool)
    
    Or with Team (Team-based delegation):
        runner = QueryExecutor(agent_name="cybersec-team", team_id=1, orchestrator_id="orch-001")
        result = await runner.query("Analyse CVE-2024-1234")  # delegates to TeamLeader
    """
    
    def __init__(
        self,
        agent_name: str = "cybersec-agent",
        session_id: str | None = None,
        mode: str = "blue",
        extra_tools: list[str] | None = None,
        pool: ClientPool | None = None,
        team_id: int | None = None,
        orchestrator_id: str | None = None,
        provider: str = "openai",
        model: str = "gpt-4",
    ) -> None:
        self.agent_name = agent_name
        self.session_id = session_id
        self.mode = mode
        self.extra_tools = extra_tools or []
        self.pool = pool
        self.team_id = team_id
        self.orchestrator_id = orchestrator_id
        self.provider = provider
        self.model = model
        self._executor: AgentExecutor | None = None
        self._team_leader: TeamLeader | None = None
        
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
    
    # ── Internal helpers ─────────────────────────────────────────────
    
    def _get_prefix(self) -> str:
        return _MODE_PREFIXES.get(self.mode, f"[MODE: {self.mode.upper()}] ")
    
    async def _get_team_leader(self) -> TeamLeader | None:
        """Lazily initialize TeamLeader (for Team-based delegation)."""
        if self.team_id is None or self.orchestrator_id is None:
            return None

        if self._team_leader is None:
            from css.modules.teams.orchestrator import TeamLeader  # TODO: implement/export TeamLeader runtime
            self._team_leader = TeamLeader(self.team_id, self.orchestrator_id)
            await self._team_leader.initialize()

        return self._team_leader

    async def _get_executor(self) -> AgentExecutor:
        """Lazily initialise AgentExecutor (provider-agnostic)."""
        if self._executor is None:
            from css.modules.agents.base import AgentExecutor
            self._executor = AgentExecutor(
                provider=self.provider,
                model=self.model,
            )
        return self._executor

    # ── Public API ───────────────────────────────────────────────────

    async def query(self, prompt: str) -> str:
        """Run a single-turn query; returns the result text.

        If team_id + orchestrator_id provided: delegates to TeamLeader.
        Otherwise: uses AgentExecutor (provider-agnostic).
        """
        from css.core.types import Query

        team_leader = await self._get_team_leader()
        if team_leader is not None:
            query_obj = Query(
                id=str(uuid.uuid4()),
                prompt=prompt,
                mode=self.mode,
                agent_name=self.agent_name,
                metadata={"created_at": datetime.now().isoformat()},
            )
            result = await team_leader.delegate(query_obj)
            return result.get("result", "") if isinstance(result, dict) else str(result)

        executor = await self._get_executor()
        full_prompt = f"{self._get_prefix()}{prompt}"

        try:
            result = await executor.execute(prompt=full_prompt)
            if hasattr(result, "session_id"):
                self.session_id = result.session_id
            return result.response if hasattr(result, "response") else str(result)
        except Exception as e:
            logger.error("QueryExecutor: AgentExecutor failed: %s", e)
            raise

    async def stream(self, prompt: str) -> AsyncGenerator[dict[str, str]]:
        """Stream a query, yielding SSE-ready dicts."""
        from css.modules.streaming.streaming import stream_query
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
        """Clean up the executor, release to pool, or shutdown TeamLeader."""
        # Close TeamLeader if active
        if self._team_leader is not None:
            await self._team_leader.shutdown()
            self._team_leader = None
        
        # Close executor's adapter if needed
        if self._executor is not None:
            # AgentExecutor doesn't hold persistent connections
            # (HttpProviderAdapter uses aiohttp session internally)
            self._executor = None
    
    def __repr__(self) -> str:
        if self.team_id:
            return (
                f"QueryExecutor(agent={self.agent_name!r}, "
                f"team_id={self.team_id}, orchestrator={self.orchestrator_id!r})"
            )
        return (
            f"QueryExecutor(agent={self.agent_name!r}, "
            f"provider={self.provider!r}, model={self.model!r}, "
            f"mode={self.mode!r}, session={self.session_id!r})"
        )
