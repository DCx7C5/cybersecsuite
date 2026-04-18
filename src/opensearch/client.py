"""Async OpenSearch client singleton."""

from __future__ import annotations

import os
from typing import Any

_client: Any = None
_OPENSEARCH_HOST = os.environ.get("OPENSEARCH_HOST", "http://localhost:9200")


def get_client() -> Any:
    """Return the module-level async OpenSearch client, creating it on first call."""
    global _client
    if _client is None:
        try:
            from opensearchpy import AsyncOpenSearch  # type: ignore[import]

            _client = AsyncOpenSearch(
                hosts=[_OPENSEARCH_HOST],
                use_ssl=False,
                verify_certs=False,
                http_compress=True,
                timeout=10,
            )
        except ImportError as exc:
            raise RuntimeError(
                "opensearch-py[async] is required. Run: uv add 'opensearch-py[async]'"
            ) from exc
    return _client


async def close_client() -> None:
    """Close the async client transport (call during app shutdown)."""
    global _client
    if _client is not None:
        try:
            await _client.close()
        except Exception:
            pass
        _client = None
