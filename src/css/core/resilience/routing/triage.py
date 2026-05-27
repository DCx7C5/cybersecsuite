"""Routing request-complexity primitives."""

from enum import Enum


class RequestComplexity(str, Enum):
    """Request complexity buckets for tier selection."""

    TRIVIAL = "TRIVIAL"
    SIMPLE = "SIMPLE"
    MODERATE = "MODERATE"
    COMPLEX = "COMPLEX"
    CRITICAL = "CRITICAL"
