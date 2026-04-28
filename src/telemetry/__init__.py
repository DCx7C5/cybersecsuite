"""
Backward compatibility shim.

This module re-exports everything from core.telemetry.
New code should import from core.telemetry directly.

Deprecation: This shim will be removed in v0.2.0
"""

from src.core.telemetry import *

__all__ = []
