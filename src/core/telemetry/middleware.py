"""Deprecated: TelemetryMiddleware moved to asgi.middleware.

This module is maintained for backward compatibility only.
New code should import from asgi.middleware instead.
"""

import warnings

from asgi.middleware import TelemetryMiddleware, _normalise

warnings.warn(
    "telemetry.middleware is deprecated; use asgi.middleware instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["TelemetryMiddleware", "_normalise"]
