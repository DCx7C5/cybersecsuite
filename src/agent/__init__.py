"""
Backward compatibility shim.

This module re-exports everything from apps.streaming.
New code should import from apps.streaming directly.

Note: This was renamed from apps.streaming to apps.streaming for semantic accuracy.

Deprecation: This shim will be removed in v0.2.0
"""

from src.apps.streaming import *

# Get exports from canonical module
try:
    from apps.streaming import __all__
except ImportError:
    __all__ = []
