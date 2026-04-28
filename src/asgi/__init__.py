"""
Backward compatibility shim.

This module re-exports everything from core.asgi.
New code should import from core.asgi directly.

Deprecation: This shim will be removed in v0.2.0
"""

from src.core.asgi import *

__all__ = []
