"""A2A (Model-to-Model) collaboration module.

Enables pause/resume streaming with external context injection between models.
Uses PREPEND strategy for highest priority context incorporation.
"""

from .enums import StreamState, ResponseInjectionStrategy
from .types import (
    A2AConfig,
    PauseRequest,
    ResponseInjection,
    StreamingController,
    StreamingState,
)

__all__ = [
    "A2AConfig",
    "StreamState",
    "ResponseInjectionStrategy",
    "PauseRequest",
    "ResponseInjection",
    "StreamingState",
    "StreamingController",
]
