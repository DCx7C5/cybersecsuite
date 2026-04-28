"""agent — High-level Claude Agent SDK integration for CyberSecSuite.

Public API:
    from agent import AgentRunner, SessionManager, getLogger, ClientPool, get_pool
    from apps.streaming.hooks import security_hook, audit_hook, cost_hook
    from apps.streaming.streaming import StreamingAdapter
"""


from logger import getLogger

from apps.streaming.runner import AgentRunner
from apps.streaming.sessions import SessionManager
from apps.streaming.client_pool import ClientPool, get_pool

__all__ = ["AgentRunner", "SessionManager", "ClientPool", "get_pool", "getLogger"]
