"""OpenObserve health + stream stats API handler."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


async def api_opensearch(request: Request) -> JSONResponse:
    """Return OpenObserve health and stream stats."""
    try:
        from openobserve.client import get_health
        from openobserve.streams import ensure_streams

        health = await get_health()
        streams = await ensure_streams()

        indices = []
        total_docs = 0
        for stream, exists in streams.items():
            if exists:
                indices.append({
                    "index": f"cybersecsuite-{stream}",
                    "docs": 0,
                    "size_mb": 0.0,
                })
                total_docs += 0

        return JSONResponse({
            "cluster": {"status": health.get("status", "unknown")},
            "indices": indices,
            "total_indices": len(indices),
            "total_docs": total_docs,
        })
    except Exception as exc:
        return JSONResponse({"error": str(exc), "cluster": None, "indices": []})