"""
Backward compatibility shim.

This module re-exports everything from core.utils.
New code should import from core.utils directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.utils import *

__all__ = []
