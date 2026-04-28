"""agent — High-level Claude Agent SDK integration for CyberSecSuite.

Public API:
    from agent import AgentRunner, SessionManager, getLogger, ClientPool, get_pool
    from apps.agent.hooks import security_hook, audit_hook, cost_hook
    from apps.agent.streaming import StreamingAdapter
"""


from logger import getLogger

from apps.agent.runner import AgentRunner
from apps.agent.sessions import SessionManager
from apps.agent.client_pool import ClientPool, get_pool

__all__ = ["AgentRunner", "SessionManager", "ClientPool", "get_pool", "getLogger"]
