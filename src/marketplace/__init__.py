"""
Backward compatibility shim.

This module re-exports everything from core.marketplace.
New code should import from core.marketplace directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.marketplace import *

__all__ = []
