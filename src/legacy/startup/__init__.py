"""Startup package for CyberSecSuite first-run detection and marketplace."""
from legacy.logger import getLogger

from startup.first_run import first_run_setup, get_marketplace, is_first_run

__all__ = ["first_run_setup", "get_marketplace", "is_first_run", "getLogger"]