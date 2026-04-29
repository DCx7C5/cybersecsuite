"""
Backward compatibility shim (deprecated).

This module previously re-exported from core.db, but core has been removed
as part of Phase 17 refactoring. src/db is the canonical location.

Migration: Import directly from src.db or src.db.models instead.
"""

# This file is now a no-op. All imports should come from src.db directly.
__all__ = []
