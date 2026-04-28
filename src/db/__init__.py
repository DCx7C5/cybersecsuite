"""
Backward compatibility shim.

This module re-exports everything from core.db.
New code should import from core.db directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.db import *

__all__ = []
