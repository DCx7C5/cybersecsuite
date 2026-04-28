"""
Backward compatibility shim.

This module re-exports everything from core.dbus.
New code should import from core.dbus directly.

Deprecation: This shim will be removed in v0.2.0
"""

from core.dbus import *

__all__ = []
