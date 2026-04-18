"""OpenSearch cluster health + index stats API handler."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


async def api_opensearch(request: Request) -> JSONResponse:
    """Return OpenSearch cluster health and per-index document/size stats."""
    try:
        from opensearch.client import get_client

        client = get_client()

        # Cluster health
        health_resp = await client.cluster.health()
        cluster_health = {
            "status": health_resp.get("status", "unknown"),
            "number_of_nodes": health_resp.get("number_of_nodes", 0),
            "active_shards": health_resp.get("active_shards", 0),
            "unassigned_shards": health_resp.get("unassigned_shards", 0),
        }

        # Index stats for our managed indices
        stats_resp = await client.indices.stats(index="cybersecsuite-*")
        indices_raw = stats_resp.get("indices", {})

        indices = []
        for idx_name, idx_stats in sorted(indices_raw.items()):
            primaries = idx_stats.get("primaries", {})
            doc_count = (primaries.get("docs") or {}).get("count", 0)
            size_bytes = (primaries.get("store") or {}).get("size_in_bytes", 0)
            indices.append({
                "index": idx_name,
                "docs": doc_count,
                "size_mb": round(size_bytes / 1024 / 1024, 2),
            })

        return JSONResponse({
            "cluster": cluster_health,
            "indices": indices,
            "total_indices": len(indices),
            "total_docs": sum(i["docs"] for i in indices),
        })
    except Exception as exc:
        return JSONResponse({"error": str(exc), "cluster": None, "indices": []})
