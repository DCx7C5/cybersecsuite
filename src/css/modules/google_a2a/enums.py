from enum import Enum


class StreamState(str, Enum):
    """Streaming lifecycle states."""

    CLEAR = "clear"  # No external request pending
    PAUSED = "paused"  # Waiting for external context
    RUNNING = "running"  # Actively streaming


class ResponseInjectionStrategy(str, Enum):
    """Strategy for injecting external response into streaming context."""

    PREPEND = "prepend"  # Inject at beginning of system context (highest priority)
    INJECT = "inject"  # Append to last assistant message (lower priority)
    CHAIN = "chain"  # Ask model to incorporate in next turn (slowest)
