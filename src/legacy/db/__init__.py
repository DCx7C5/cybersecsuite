"""
Backward compatibility shim.

This module re-exports everything from core.db.
New code should import from core.db directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.db import *

# Get exports from canonical module
try:
    from core.db import __all__
except ImportError:
    __all__ = []
