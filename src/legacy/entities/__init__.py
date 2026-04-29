"""
Backward compatibility shim.

This module re-exports everything from core.entities.
New code should import from core.entities directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.entities import *

# Get exports from canonical module
try:
    from core.entities import __all__
except ImportError:
    __all__ = []
