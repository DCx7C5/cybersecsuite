"""
Backward compatibility shim.

This module re-exports everything from core.routes.
New code should import from core.routes directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.routes import *

__all__ = []
