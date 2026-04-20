"""Async OpenObserve client singleton."""

from __future__ import annotations

import os
from typing import Any

import httpx

_client: httpx.AsyncClient | None = None

OPENOBSERVE_HOST = os.environ.get("OPENOBSERVE_HOST", "http://localhost:5080")
OPENOBSERVE_ORG = os.environ.get("OPENOBSERVE_ORG", "default")
OPENOBSERVE_EMAIL = os.environ.get("OPENOBSERVE_EMAIL", "admin@cybersec.local")
OPENOBSERVE_PASSWORD = os.environ.get("OPENOBSERVE_PASSWORD", "cYb3rS3c!")


def get_client() -> httpx.AsyncClient:
    """Return the module-level async httpx client, creating it on first call."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=OPENOBSERVE_HOST,
            auth=(OPENOBSERVE_EMAIL, OPENOBSERVE_PASSWORD),
            timeout=10.0,
        )
    return _client


async def close_client() -> None:
    """Close the async client transport (call during app shutdown)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def get_health() -> dict[str, Any]:
    """Check OpenObserve health."""
    client = get_client()
    try:
        resp = await client.get("/healthz")
        if resp.status_code == 200:
            return {"status": "healthy", "host": OPENOBSERVE_HOST}
        return {"status": "unhealthy", "host": OPENOBSERVE_HOST, "error": resp.text[:200]}
    except Exception as e:
        return {"status": "unavailable", "host": OPENOBSERVE_HOST, "error": str(e)}