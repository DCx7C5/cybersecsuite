"""
Backward compatibility shim.

This module re-exports everything from core.types.entities.
New code should import from core.types.entities directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.types.entities import *

# Get exports from canonical module
try:
    from core.types.entities import __all__
except ImportError:
    __all__ = []
