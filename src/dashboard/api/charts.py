"""Chart data API — serves JSON datasets for Chart.js / ECharts panels."""
from __future__ import annotations

import datetime
from starlette.requests import Request
from starlette.responses import JSONResponse

_SEVERITIES = ("critical", "high", "medium", "low", "info")


def _days_ago(n: int) -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=n)


def _day_labels(n: int) -> list[str]:
    return [
        (_days_ago(n - 1 - i)).strftime("%m/%d")
        for i in range(n)
    ]


async def api_charts(request: Request) -> JSONResponse:
    """GET /api/charts/{name}?range=7d"""
    name = request.path_params.get("name", "")
    range_days = max(1, min(90, int(request.query_params.get("range", "7").replace("d", ""))))

    try:
        if name == "provider-share":
            return await _provider_share()
        if name == "token-trend":
            return await _token_trend(range_days)
        if name == "ioc-types":
            return await _ioc_types()
        if name == "ioc-timeline":
            return await _ioc_timeline(range_days)
        if name == "findings-heatmap":
            return await _findings_heatmap(range_days)
        if name == "mitre-heatmap":
            return await _mitre_heatmap()
        if name == "latency-percentiles":
            return await _latency_percentiles()
        return JSONResponse({"error": f"Unknown chart: {name}"}, status_code=404)
    except Exception as exc:
        return JSONResponse({"labels": [], "datasets": [], "error": str(exc)})


# ── Individual chart builders ─────────────────────────────────────────────────

async def _provider_share() -> JSONResponse:
    try:
        from ai_proxy.routing.combo import get_usage_counts
        counts = get_usage_counts()
        labels = list(counts.keys()) or ["No data"]
        data = [counts[k] for k in labels] or [1]
    except Exception:
        labels, data = ["No data"], [1]
    return JSONResponse({"labels": labels, "datasets": [{"data": data}]})


async def _token_trend(days: int) -> JSONResponse:
    labels = _day_labels(days)
    try:
        from openobserve.client import get_client, OPENOBSERVE_ORG
        client = get_client()
        data: list[int] = []
        for i in range(days):
            start = _days_ago(days - i)
            stream = f"cybersecsuite-api-usage-{start.strftime('%Y.%m.%d')}"
            resp = await client.get(f"/api/{OPENOBSERVE_ORG}/{stream}")
            if resp.status_code == 200:
                data.append(int(resp.json().get("stats", {}).get("doc_num", 0)))
            else:
                data.append(0)
    except Exception:
        data = [0] * days
    return JSONResponse({"labels": labels, "datasets": [{"label": "Requests", "data": data}]})


async def _ioc_types() -> JSONResponse:
    try:
        from db.models.ioc import IOC
        all_types: list[str] = []
        async for ioc in IOC.all().only("ioc_type"):
            t = str(getattr(ioc, "ioc_type", "unknown"))
            if t not in all_types:
                all_types.append(t)
        counts = {t: await IOC.filter(ioc_type=t).count() for t in all_types}
        labels = list(counts.keys()) or ["No data"]
        data = [counts[k] for k in labels] or [1]
    except Exception:
        labels, data = ["No data"], [1]
    return JSONResponse({"labels": labels, "datasets": [{"data": data}]})


async def _ioc_timeline(days: int) -> JSONResponse:
    try:
        from db.models.ioc import IOC
        cutoff = _days_ago(days)
        iocs = await IOC.filter(created_at__gte=cutoff).only(
            "ioc_type", "created_at"
        ).values("ioc_type", "created_at")
        # Collect unique types as Y-axis categories
        types: list[str] = sorted({str(row["ioc_type"]) for row in iocs})
        # Build [timestamp_ms, type_index, 1] triples for ECharts scatter
        points: list[list] = []
        for row in iocs:
            ts = row["created_at"]
            if hasattr(ts, "timestamp"):
                ms = int(ts.timestamp() * 1000)
            else:
                ms = 0
            idx = types.index(str(row["ioc_type"])) if str(row["ioc_type"]) in types else 0
            points.append([ms, idx, 1])
        labels = types or ["unknown"]
    except Exception:
        labels, points = ["unknown"], []
    return JSONResponse({"labels": labels, "datasets": [{"data": points}]})


async def _findings_heatmap(days: int) -> JSONResponse:
    """Returns data for ECharts heatmap: [day_index, sev_index, count]."""
    labels = _day_labels(days)
    try:
        from db.models.investigation import Finding
        _cutoff = _days_ago(days)
        matrix: list[list] = []
        max_val = 1
        for d_idx, day_label in enumerate(labels):
            day_start = _days_ago(days - 1 - d_idx)
            day_end = day_start + datetime.timedelta(days=1)
            for s_idx, sev in enumerate(_SEVERITIES):
                count = await Finding.filter(
                    severity=sev,
                    created_at__gte=day_start,
                    created_at__lt=day_end,
                ).count()
                matrix.append([d_idx, s_idx, count])
                max_val = max(max_val, count)
        return JSONResponse({
            "labels": labels,
            "severities": list(_SEVERITIES),
            "max": max_val,
            "datasets": [{"data": matrix}],
        })
    except Exception:
        return JSONResponse({"labels": labels, "severities": list(_SEVERITIES), "max": 1, "datasets": [{"data": []}]})


async def _mitre_heatmap() -> JSONResponse:
    """MITRE technique frequency: techniques × tactic buckets."""
    try:
        from db.models.mitre_technique import MitreTechnique
        techniques = await MitreTechnique.all().only(
            "technique_id", "name", "tactics"
        ).values("technique_id", "name", "tactics")
        tactic_set: set[str] = set()
        for t in techniques:
            raw = t.get("tactics") or []
            if isinstance(raw, list):
                tactic_set.update(str(x) for x in raw if x)
            else:
                tactic_set.add(str(raw) if raw else "unknown")
        tactics = sorted(tactic_set) or ["unknown"]
        tech_ids = [str(t["technique_id"]) for t in techniques]
        counts: list[list] = []
        max_val = 1
        for t_idx, tech in enumerate(techniques):
            raw = tech.get("tactics") or []
            tac = (raw[0] if isinstance(raw, list) and raw else str(raw)) or "unknown"
            tac_idx = tactics.index(tac) if tac in tactics else 0
            count = 1
            counts.append([tac_idx, t_idx, count])
            max_val = max(max_val, count)
        return JSONResponse({
            "labels": tech_ids[:50],  # cap at 50 for readability
            "tactics": tactics,
            "max": max_val,
            "datasets": [{"data": counts[:50]}],
        })
    except Exception:
        return JSONResponse({"labels": [], "tactics": [], "max": 1, "datasets": [{"data": []}]})


async def _latency_percentiles() -> JSONResponse:
    """p50/p95/p99 latency from in-process telemetry ring buffer."""
    labels: list[str] = []
    p50_data: list[float] = []
    p95_data: list[float] = []
    p99_data: list[float] = []
    try:
        from telemetry.collector import collector as tc
        snapshots = getattr(tc, "_snapshots", []) or []
        for snap in snapshots[-20:]:
            labels.append(snap.get("ts", ""))
            p50_data.append(snap.get("p50", 0))
            p95_data.append(snap.get("p95", 0))
            p99_data.append(snap.get("p99", 0))
        if not labels:
            # Fallback: current single snapshot
            metrics = tc.get_metrics() if hasattr(tc, "get_metrics") else {}
            labels = ["now"]
            p50_data = [metrics.get("p50_ms", 0)]
            p95_data = [metrics.get("p95_ms", 0)]
            p99_data = [metrics.get("p99_ms", 0)]
    except Exception:
        labels = ["n/a"]
        p50_data = p95_data = p99_data = [0]
    return JSONResponse({
        "labels": labels,
        "datasets": [
            {"label": "p50", "data": p50_data},
            {"label": "p95", "data": p95_data},
            {"label": "p99", "data": p99_data},
        ],
    })
