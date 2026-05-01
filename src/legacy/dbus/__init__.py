"""DBus integration for desktop notifications and signals."""


from legacy.logger import getLogger

from .notifier import DbusNotifier, get_notifier

__all__ = ["DbusNotifier", "get_notifier", "getLogger"]
