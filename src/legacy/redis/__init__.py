"""
Backward compatibility shim.

This module re-exports everything from core.redis.
New code should import from core.redis directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.redis import *

# Get exports from canonical module
try:
    from core.redis import __all__
except ImportError:
    __all__ = []
