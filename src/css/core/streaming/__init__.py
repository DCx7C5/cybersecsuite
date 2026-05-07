"""agents — High-level Claude Agent SDK integration for CyberSecSuite.

Public API:
    from agents import QueryExecutor, SessionManager, getLogger, ClientPool, get_pool
    from modules.streaming.hooks import security_hook, audit_hook, cost_hook
    from modules.streaming.streaming import StreamingAdapter
"""

from css.core.logger import getLogger

logger = getLogger(__name__)

from css.modules.streaming.runner import QueryExecutor
from css.modules.streaming.sessions import SessionManager
from css.core.orchestration.client_pool import ClientPool, get_pool

__all__ = ["QueryExecutor", "SessionManager", "ClientPool", "get_pool", "logger"]
