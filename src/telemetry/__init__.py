"""
Backward compatibility shim.

This module re-exports everything from core.telemetry.
New code should import from core.telemetry directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.telemetry import *

# Get exports from canonical module
try:
    from core.telemetry import __all__
except ImportError:
    __all__ = []
