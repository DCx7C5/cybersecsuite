"""
Backward compatibility shim.

This module re-exports everything from core.endpoints.
New code should import from core.endpoints directly.

Deprecation: This shim will be removed in v0.2.0
"""

from src.core.endpoints import *

__all__ = []
