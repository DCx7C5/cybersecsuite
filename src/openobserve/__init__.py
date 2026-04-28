"""
Backward compatibility shim.

This module re-exports everything from core.openobserve.
New code should import from core.openobserve directly.

Deprecation: This shim will be removed in v0.2.0
"""

from src.core.openobserve import *

__all__ = []
