"""
Backward compatibility shim.

This module re-exports everything from core.registries.
New code should import from core.registries directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.registries import *

__all__ = []
