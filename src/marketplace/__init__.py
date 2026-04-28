"""
Backward compatibility shim.

This module re-exports everything from core.marketplace.
New code should import from core.marketplace directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.marketplace import *

# Get exports from canonical module
try:
    from core.marketplace import __all__
except ImportError:
    __all__ = []
