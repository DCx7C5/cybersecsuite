"""
Backward compatibility shim.

This module re-exports everything from core.communicators.
New code should import from core.communicators directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.communicators import *

__all__ = []
