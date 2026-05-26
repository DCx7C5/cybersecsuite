"""Shared DB helper utilities."""

from __future__ import annotations

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def coerce_int(value: object, *, field: str) -> int:
    """Coerce a value to int with a clear field-scoped error."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer value") from exc


__all__ = ["utc_now", "coerce_int"]
