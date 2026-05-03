"""agents — High-level Claude Agent SDK integration for CyberSecSuite.

Public API:
    from agents import AgentRunner, SessionManager, getLogger, ClientPool, get_pool
    from modules.streaming.hooks import security_hook, audit_hook, cost_hook
    from modules.streaming.streaming import StreamingAdapter
"""


from legacy.logger import getLogger

from modules.streaming.runner import AgentRunner
from modules.streaming.sessions import SessionManager
from core.orchestration.client_pool import ClientPool, get_pool

__all__ = ["AgentRunner", "SessionManager", "ClientPool", "get_pool", "getLogger"]
