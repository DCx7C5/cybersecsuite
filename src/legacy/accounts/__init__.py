"""Account management package for API provider keys.

Exports:
    AccountManager  — singleton for managing API accounts
    AccountEntry    — Pydantic model for account metadata
    getLogger       — module-level logger
"""
from legacy.logger import getLogger

from accounts.manager import AccountManager

__all__ = ["AccountManager", "getLogger"]