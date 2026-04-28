"""
Backward compatibility shim.

This module re-exports everything from core.memory.
New code should import from core.memory directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.memory import *

__all__ = []
