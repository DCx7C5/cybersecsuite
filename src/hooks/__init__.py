"""
Backward compatibility shim.

This module re-exports everything from core.hooks.
New code should import from core.hooks directly.

Deprecation: This shim will be removed in v0.2.0
"""

from src.core.hooks import *

__all__ = []
