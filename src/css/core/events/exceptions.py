"""Event system exceptions."""


class EventError(Exception):
    """Base exception for event system."""
    pass


class HookRegistrationError(EventError):
    """Error registering a hook."""
    pass


class HookTimeoutError(EventError):
    """Hook execution timed out."""
    pass


class EventBusError(EventError):
    """Error emitting event."""
    pass
