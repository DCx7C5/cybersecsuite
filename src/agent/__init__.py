"""agent — High-level Claude Agent SDK integration for CyberSecSuite.

Public API:
    from agent import AgentRunner, SessionManager
    from agent.hooks import security_hook, audit_hook, cost_hook
    from agent.streaming import StreamingAdapter
"""
from __future__ import annotations

from agent.runner import AgentRunner
from agent.sessions import SessionManager

__all__ = ["AgentRunner", "SessionManager"]
