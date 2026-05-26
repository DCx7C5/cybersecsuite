"""Compatibility exports for the shared tool executor runtime."""

from css.core.tools.executor import AgentToolExecutor as _AgentToolExecutor, get_executor as _get_executor

AgentToolExecutor = _AgentToolExecutor
get_executor = _get_executor
