"""
Backward compatibility shim.

This module re-exports everything from core.cssmcp.
New code should import from core.cssmcp directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.cssmcp import *

# Get exports from canonical module
try:
    from core.cssmcp import __all__
except ImportError:
    __all__ = []
