"""Streaming — High-level Claude Agent SDK integration for CyberSecSuite.

Public API:
    from streaming import QueryExecutor, SessionManager, getLogger, ClientPool, get_pool
    from core.streaming.hooks import security_hook, audit_hook, cost_hook
    from core.streaming.streaming import StreamingAdapter
"""

from css.core.logger import getLogger
from css.core.streaming.runner import QueryExecutor
from css.core.streaming.sessions import SessionManager
from css.core.streaming.client_pool import ClientPool, get_pool

logger = getLogger(__name__)

__all__ = ["QueryExecutor", "SessionManager", "ClientPool", "get_pool", "logger"]
