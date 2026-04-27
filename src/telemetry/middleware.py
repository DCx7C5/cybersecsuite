"""Deprecated: TelemetryMiddleware moved to proxy.middleware.

This module is maintained for backward compatibility only.
New code should import from proxy.middleware instead.
"""

import warnings

from proxy.middleware import TelemetryMiddleware, _normalise

warnings.warn(
    "telemetry.middleware is deprecated; use proxy.middleware instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["TelemetryMiddleware", "_normalise"]
