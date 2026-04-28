"""
Backward compatibility shim.

This module re-exports everything from core.hooks.
New code should import from core.hooks directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.hooks import *

# Get exports from canonical module
try:
    from core.hooks import __all__
except ImportError:
    __all__ = []
