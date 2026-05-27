"""Hook event types and context — foundational contracts for hook system.

Converted to msgspec.Struct for faster serialization.
"""

import msgspec

from css.core.types.base_enums import HookErrorStrategy


class HookContext(msgspec.Struct, frozen=True, kw_only=True):
    """Metadata passed to every hook execution."""

    correlation_id: str
    session_id: str
    timestamp: float
    tool_use_id: str | None = None
    agent_id: str | None = None
