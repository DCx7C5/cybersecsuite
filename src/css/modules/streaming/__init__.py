"""modules.streaming — High-level agent streaming runner.

QueryExecutor lives here (not in core) because it depends on:
- modules/agents (AgentExecutor)
- modules/teams (TeamLeader)

Core streaming infra (ClientPool, SessionManager, hooks) stays in core/streaming/.
"""

from .runner import QueryExecutor

__all__ = ["QueryExecutor"]
