"""
Backward compatibility shim.

This module re-exports everything from core.tools.
New code should import from core.tools directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.tools import *

# Get exports from canonical module
try:
    from core.tools import __all__
except ImportError:
    __all__ = []
