"""Agent tool executor — wires AgentRegistry → ToolRegistry → PermissionChecker → EventBus.

This is the Phase 5 integration point for T5.1.  It keeps the agent, tool,
permission, and event layers loosely coupled: none of them import each other
directly; the executor is the only place that knows about all four.

Usage::

    from css.modules.agents.executor import AgentToolExecutor, get_executor

    executor = get_executor()
    result = await executor.execute_tool(
        agent_id="agent-123",
        tool_id="openai:code_interpreter",
        params={"code": "print('hello')"},
        scope=scope_context,          # optional — skipped if None
    )
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from css.core.tools.base import BaseToolRegistry
from css.core.tools.exceptions import ToolNotFoundError, ToolExecutionError
from css.core.events.instrument import instrument

logger = logging.getLogger(__name__)


class AgentToolExecutor:
    """Executes tools on behalf of agents with permission checks and event tracking.

    Attributes:
        _registry: Shared ToolRegistry singleton.
        _checker: Optional PermissionChecker instance (None → skip perm checks).
    """

    def __init__(self, permission_checker=None):
        self._registry = get_tool_registry()
        self._checker = permission_checker

    async def execute_tool(
        self,
        agent_id: str,
        tool_id: str,
        params: dict[str, Any],
        scope: Optional[Any] = None,
    ) -> dict[str, Any]:
        """Execute *tool_id* on behalf of *agent_id*.

        Steps:
          1. Resolve the tool from the registry — raise ``ToolNotFoundError`` if missing.
          2. Check permissions via ScopeContext (skipped when scope is None).
          3. Emit ``tool.call.start`` event.
          4. Run the tool's callable (``ManagedTool.schema.fn`` if present, else raise).
          5. Emit ``tool.call.complete`` or ``tool.call.error`` event.
          6. Update registry call counters.

        Args:
            agent_id: Identifier of the calling agent (for audit trail).
            tool_id: Canonical tool identifier in ``provider:name`` format.
            params: Tool input parameters as a plain dict.
            scope: Optional :class:`~css.modules.permissions.types.ScopeContext`.
                   When provided, permission check is enforced.

        Returns:
            A ``{"result": ..., "duration_ms": float}`` dict.

        Raises:
            ToolNotFoundError: Tool is not registered or is disabled.
            PermissionDenied: Agent's scope lacks tool permission.
            ToolExecutionError: Tool callable raised an exception.
        """
        managed = self._registry.tools.get(tool_id)
        if managed is None or not managed.is_available:
            raise ToolNotFoundError(tool_id=tool_id)

        # Permission gate — only when a ScopeContext is supplied
        if scope is not None and self._checker is not None:
            self._checker.require_tool(scope, tool_id)

        async with instrument(
            "tool.call",
            agent_id=agent_id,
            tool_id=tool_id,
        ) as event_payload:
            fn = getattr(managed.schema, "fn", None)
            if fn is None:
                # Builtin provider tools (openai:code_interpreter etc.) are
                # specification-only in Phase 5 — no callable yet.  Return a
                # stub result so upstream code can proceed.
                logger.debug(
                    "tool '%s' has no fn; returning spec-only stub result", tool_id
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
                import inspect
                if inspect.iscoroutinefunction(fn):
                    raw = await fn(**params)
                else:
                    raw = fn(**params)
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
        scope: Optional[Any] = None,
    ) -> list[dict[str, Any]]:
        """Execute all component tools of a HybridToolDefinition.

        Runs component tools sequentially (Phase 5 only supports sequential).
        Parallel / conditional strategies are deferred to Phase 6.

        Args:
            agent_id: Identifier of the calling agent.
            hybrid_tool_id: Hybrid tool identifier (``hybrid:name`` format).
            params: Shared input parameters passed to every component tool.
            scope: Optional ScopeContext for permission checks.

        Returns:
            List of result dicts, one per component tool.

        Raises:
            ToolNotFoundError: Hybrid tool not registered.
            ToolExecutionError: Any component tool fails.
        """
        hybrid = self._registry.hybrid_tools.get(hybrid_tool_id)
        if hybrid is None or not hybrid.is_available:
            raise ToolNotFoundError(tool_id=hybrid_tool_id)

        results = []
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


# Module-level singleton
_executor: Optional[AgentToolExecutor] = None


def get_executor(permission_checker=None) -> AgentToolExecutor:
    """Return the global AgentToolExecutor singleton.

    Args:
        permission_checker: Injected on first call.  Ignored on subsequent calls
            (singleton is reused).  Pass ``None`` to skip permission checks.
    """
    global _executor
    if _executor is None:
        _executor = AgentToolExecutor(permission_checker=permission_checker)
    return _executor


__all__ = ["AgentToolExecutor", "get_executor"]
