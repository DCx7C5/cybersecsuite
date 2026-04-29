"""
Backward compatibility shim.

This module re-exports everything from core.endpoints.
New code should import from core.endpoints directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.endpoints import *

# Get exports from canonical module
try:
    from core.endpoints import __all__
except ImportError:
    __all__ = []
