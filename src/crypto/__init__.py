"""
Backward compatibility shim.

This module re-exports everything from core.crypto.
New code should import from core.crypto directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.crypto import *

__all__ = []
