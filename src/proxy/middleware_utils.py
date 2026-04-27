"""Common middleware utilities shared across proxy, telemetry, and scope middleware."""

import re
from typing import List, Tuple

PathPattern = Tuple[re.Pattern, str]


def should_skip_path(path: str, skip_prefixes: List[str]) -> bool:
    """Check if a path should be skipped based on prefix list.

    Args:
        path: Request path to check
        skip_prefixes: List of path prefixes to skip (e.g., ["/health", "/static"])

    Returns:
        True if path matches any skip prefix, False otherwise
    """
    return any(path.startswith(p) for p in skip_prefixes)


def normalize_path_patterns(path: str, patterns: List[PathPattern]) -> str:
    """Normalize path by replacing patterns (e.g., numeric IDs with placeholders).

    Useful for reducing cardinality explosion in metrics/logs by replacing
    dynamic segments (UUIDs, numeric IDs) with generic placeholders.

    Args:
        path: Path to normalize
        patterns: List of (compiled_pattern, replacement) tuples

    Returns:
        Normalized path with patterns replaced

    Example:
        >>> patterns = [
        ...     (re.compile(r"/\\d{1,18}(?=/|$)"), "/{id}"),
        ...     (re.compile(r"/[0-9a-fA-F-]{32,}(?=/|$)"), "/{uuid}"),
        ... ]
        >>> normalize_path_patterns("/api/users/12345/sessions/abc123", patterns)
        '/api/users/{id}/sessions/{uuid}'
    """
    for pat, rep in patterns:
        path = pat.sub(rep, path)
    return path
