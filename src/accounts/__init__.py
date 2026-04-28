"""
Backward compatibility shim.

This module re-exports everything from core.accounts.
New code should import from core.accounts directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.accounts import *

__all__ = []
