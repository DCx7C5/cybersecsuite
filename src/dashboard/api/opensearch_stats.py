"""OpenObserve health + stream stats API handler."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


async def api_opensearch(request: Request) -> JSONResponse:
    """Return OpenObserve health and stream stats."""
    try:
        from openobserve.client import get_client, get_health, OPENOBSERVE_ORG
        from openobserve.streams import STREAMS

        health = await get_health()
        client = get_client()
        org = OPENOBSERVE_ORG

        indices = []
        total_docs = 0
        for stream in STREAMS:
            try:
                resp = await client.get(f"/api/{org}/{stream}")
                if resp.status_code == 200:
                    data = resp.json()
                    stats = data.get("stats", {})
                    doc_num = stats.get("doc_num", 0)
                    storage_size = stats.get("storage_size", 0)
                    size_mb = round(storage_size / (1024 * 1024), 3) if storage_size else 0.0
                    indices.append({
                        "index": f"cybersecsuite-{stream}",
                        "docs": doc_num,
                        "size_mb": size_mb,
                    })
                    total_docs += doc_num
                else:
                    indices.append({"index": f"cybersecsuite-{stream}", "docs": 0, "size_mb": 0.0})
            except Exception:
                indices.append({"index": f"cybersecsuite-{stream}", "docs": 0, "size_mb": 0.0})

        return JSONResponse({
            "cluster": {"status": health.get("status", "unknown")},
            "indices": indices,
            "total_indices": len(indices),
            "total_docs": total_docs,
        })
    except Exception as exc:
        return JSONResponse({"error": str(exc), "cluster": None, "indices": []})