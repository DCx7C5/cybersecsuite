"""
Backward compatibility shim.

This module re-exports everything from core.types.endpoints.
New code should import from core.types.endpoints directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.types.endpoints import *

# Get exports from canonical module
try:
    from core.types.endpoints import __all__
except ImportError:
    __all__ = []
