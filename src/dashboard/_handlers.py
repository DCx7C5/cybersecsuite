"""Dashboard API + SSE request handlers — thin re-export shim.

All handler functions now live in ``dashboard.api.*`` submodules.
This module re-exports every public name so that existing imports such as
``from dashboard._handlers import api_overview`` continue to work.
"""
from dashboard.api import *  # noqa: F401,F403

