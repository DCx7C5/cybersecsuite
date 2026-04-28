"""
Backward compatibility shim.

This module re-exports everything from core.tools.
New code should import from core.tools directly.

Deprecation: This shim will be removed in v0.2.0
"""

from src.core.tools import *

__all__ = []
