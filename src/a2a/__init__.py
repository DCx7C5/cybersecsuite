"""
Backward compatibility shim.

This module re-exports everything from core.a2a.
New code should import from core.a2a directly.

Deprecation: This shim will be removed in v0.2.0
"""

from src.core.a2a import *

__all__ = []
