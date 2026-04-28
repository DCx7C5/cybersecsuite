"""
Backward compatibility shim.

This module re-exports everything from core.checks.
New code should import from core.checks directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.checks import *

# Get exports from canonical module
try:
    from core.checks import __all__
except ImportError:
    __all__ = []
