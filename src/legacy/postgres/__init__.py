"""
Backward compatibility shim.

This module re-exports everything from core.postgres.
New code should import from core.postgres directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.postgres import *

# Get exports from canonical module
try:
    from core.postgres import __all__
except ImportError:
    __all__ = []
