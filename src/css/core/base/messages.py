"""Base message type — msgspec.Struct (Phase 6 P1)."""

from css.core.logger import getLogger

import msgspec

from .enums import MessageRole

logger = getLogger(__name__)


class BaseMessage(msgspec.Struct, frozen=True, kw_only=True):
    """A message in the conversation."""

    role: MessageRole
    content: str = ""
    name: str | None = None
    tool_calls: list[dict[str, str]] = msgspec.field(default_factory=list)
    tool_call_id: str | None = None
