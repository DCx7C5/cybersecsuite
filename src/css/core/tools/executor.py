"""Shared tool execution runtime used by agents and chat flows."""

import inspect
from functools import lru_cache
from typing import Any

from css.core.events.instrument import instrument
from css.core.logger import getLogger
from css.core.tools.base import get_tool_registry
from css.core.tools.exceptions import ToolExecutionError, ToolNotFoundError

logger = getLogger(__name__)


class AgentToolExecutor:
    """Executes tools on behalf of agents with permission checks and audit hooks."""

    def __init__(self, permission_checker: object | None = None) -> None:
        self._registry = get_tool_registry()
        self._checker = permission_checker

    async def execute_tool(
        self,
        agent_id: str,
        tool_id: str,
        params: dict[str, Any],
        scope: object | None = None,
    ) -> dict[str, Any]:
        """Execute a single registered tool."""

        managed = self._registry.tools.get(tool_id)
        if managed is None or not managed.is_available:
            raise ToolNotFoundError(tool_id=tool_id)

        if scope is not None and self._checker is not None:
            self._checker.require_tool(scope, tool_id)

        async with instrument(
            "tool.call",
            agent_id=agent_id,
            tool_id=tool_id,
        ) as event_payload:
            fn = getattr(managed.schema, "fn", None)
            if fn is None:
                logger.debug(
                    "tool '%s' has no fn; returning spec-only stub result",
                    tool_id,
                )
                managed.mark_called()
                result = {
                    "stub": True,
                    "tool_id": tool_id,
                    "params": params,
                    "note": "Builtin spec-only tool — no callable in Phase 5",
                }
                event_payload["result"] = result
                return result

            try:
                raw = await fn(**params) if inspect.iscoroutinefunction(fn) else fn(**params)
            except Exception as exc:
                managed.mark_error(str(exc))
                raise ToolExecutionError(
                    message=str(exc),
                    tool_id=tool_id,
                ) from exc

            managed.mark_called()
            result = raw if isinstance(raw, dict) else {"result": raw}
            event_payload["result"] = result
            return result

    async def execute_hybrid_tool(
        self,
        agent_id: str,
        hybrid_tool_id: str,
        params: dict[str, Any],
        scope: object | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a hybrid tool sequentially across its component tools."""

        hybrid = self._registry.hybrid_tools.get(hybrid_tool_id)
        if hybrid is None or not hybrid.is_available:
            raise ToolNotFoundError(tool_id=hybrid_tool_id)

        results: list[dict[str, Any]] = []
        async with instrument(
            "tool.call",
            agent_id=agent_id,
            tool_id=hybrid_tool_id,
            is_hybrid=True,
        ) as event_payload:
            for component_id in hybrid.schema.component_tools:
                result = await self.execute_tool(
                    agent_id=agent_id,
                    tool_id=component_id,
                    params=params,
                    scope=scope,
                )
                results.append(result)

            event_payload["component_results"] = results
        return results


@lru_cache(maxsize=1)
def _cached_executor() -> AgentToolExecutor:
    return AgentToolExecutor()


def get_executor(permission_checker: object | None = None) -> AgentToolExecutor:
    """Return a shared AgentToolExecutor instance."""

    executor = _cached_executor()
    if permission_checker is not None and executor._checker is None:
        executor._checker = permission_checker
    return executor
