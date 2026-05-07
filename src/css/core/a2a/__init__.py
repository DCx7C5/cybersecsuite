"""Core A2A protocol -- shared enums for css_a2a and google_a2a."""

from .enums import MessageRole, PartType, ResponseInjectionStrategy, StreamState, TaskState

__all__ = [
    "TaskState",
    "MessageRole",
    "PartType",
    "StreamState",
    "ResponseInjectionStrategy",
]
