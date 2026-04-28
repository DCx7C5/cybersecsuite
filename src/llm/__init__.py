"""
Backward compatibility shim.

This module re-exports everything from core.llm.
New code should import from core.llm directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.llm import *

__all__ = []
