"""
Backward compatibility shim.

This module re-exports everything from core.ai_proxy.
New code should import from core.ai_proxy directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.ai_proxy import *

__all__ = []
