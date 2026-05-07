"""Hook event types and context — foundational contracts for hook system.

Converted to msgspec.Struct (Phase 6 P1) for faster serialization.
"""

import msgspec
from enum import Enum
from typing import Optional


class HookContext(msgspec.Struct, frozen=True):
    """Metadata passed to every hook execution.
    
    Attributes:
        correlation_id: Unique request correlation ID (links logs across services)
        session_id: CyberSecSuite session ID
        timestamp: Hook execution start timestamp (seconds since epoch)
        tool_use_id: Claude SDK tool_use_id (optional, may not apply to all hooks)
        agent_id: Agent identifier (optional, may not apply to all hooks)
    """
    correlation_id: str
    session_id: str
    timestamp: float
    tool_use_id: Optional[str] = None
    agent_id: Optional[str] = None


class HookErrorStrategy(str, Enum):
    """How to handle errors in hook execution.
    
    Values:
        PRESERVE_EXISTING: Don't break on hook failure (default, safest)
        LOG: Log errors to audit but don't propagate
        WARN: Log warnings to audit but don't propagate
    """
    PRESERVE_EXISTING = "preserve"
    LOG = "log"
    WARN = "warn"


__all__ = ["HookContext", "HookErrorStrategy"]
