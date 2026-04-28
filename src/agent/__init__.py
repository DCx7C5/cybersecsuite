"""
Backward compatibility shim.

This module re-exports everything from apps.agent.
New code should import from apps.agent directly.

Deprecation: This shim will be removed in v0.2.0
"""

from src.apps.agent import *

__all__ = []
