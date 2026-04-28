"""
Backward compatibility shim.

This module re-exports everything from core.startup.
New code should import from core.startup directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.startup import *

# Get exports from canonical module
try:
    from core.startup import __all__
except ImportError:
    __all__ = []
