"""
Backward compatibility shim.

This module re-exports everything from core.entities.
New code should import from core.entities directly.

Deprecation: This shim will be removed in v0.2.0
"""

from src.core.entities import *

__all__ = []
