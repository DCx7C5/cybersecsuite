"""
Backward compatibility shim.

This module re-exports everything from core.startup.
New code should import from core.startup directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.startup import *

__all__ = []
