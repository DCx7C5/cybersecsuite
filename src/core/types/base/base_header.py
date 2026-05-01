"""Abstract base header — minimal metadata for all domain entities."""

from dataclasses import dataclass


@dataclass
class BaseHeader:
    """Root metadata header for all domain entities."""
    name: str
    description: str


__all__ = ["BaseHeader"]
