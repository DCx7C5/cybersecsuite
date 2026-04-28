"""
Backward compatibility shim.

This module re-exports everything from core.asgi.
New code should import from core.asgi directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.asgi import *

# Get exports from canonical module
try:
    from core.asgi import __all__
except ImportError:
    __all__ = []
