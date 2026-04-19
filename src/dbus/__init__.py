"""DBus integration for desktop notifications and signals."""
from __future__ import annotations

from .notifier import DbusNotifier, get_notifier

__all__ = ["DbusNotifier", "get_notifier"]
