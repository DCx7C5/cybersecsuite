"""core.streaming — Streaming infrastructure primitives.

Provides: ClientPool, SessionManager, get_pool.
QueryExecutor lives in modules/streaming/runner.py (depends on agent modules).

Public API:
    from css.core.streaming import ClientPool, get_pool, SessionManager
    from css.core.streaming.hooks import security_hook, audit_hook, cost_hook
"""

import logging

from css.core.streaming.sessions import SessionManager
from css.core.streaming.client_pool import ClientPool, get_pool

logger = logging.getLogger(__name__)

__all__ = ["SessionManager", "ClientPool", "get_pool", "logger"]
