"""agent — High-level Claude Agent SDK integration for CyberSecSuite.

Public API:
    from agent import AgentRunner, SessionManager, getLogger, ClientPool, get_pool
    from agent.hooks import security_hook, audit_hook, cost_hook
    from agent.streaming import StreamingAdapter
"""


from logger import getLogger

from agent.runner import AgentRunner
from agent.sessions import SessionManager
from agent.client_pool import ClientPool, get_pool

__all__ = ["AgentRunner", "SessionManager", "ClientPool", "get_pool", "getLogger"]
