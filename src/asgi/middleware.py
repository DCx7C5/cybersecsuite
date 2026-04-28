"""Backward compatibility shim for asgi.middleware module."""

from core.asgi.middleware import *

__all__ = []

try:
    from core.asgi.middleware import __all__
except ImportError:
    __all__ = []
