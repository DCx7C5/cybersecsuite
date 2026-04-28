"""
Backward compatibility shim.

This module re-exports everything from core.postgres.
New code should import from core.postgres directly.

Deprecation: This shim will be removed in v0.2.0
"""

from src.core.postgres import *

__all__ = []
