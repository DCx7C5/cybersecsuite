"""Backward-compatibility shim — use db.intel instead."""
from db.intel import BootstrapStats, bootstrap_intelligence_async, get_intelligence_root

__all__ = [
    "BootstrapStats",
    "bootstrap_intelligence_async",
    "get_intelligence_root",
]
