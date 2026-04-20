"""Stream management for CyberSecSuite OpenObserve."""

from __future__ import annotations

from openobserve.client import get_client, OPENOBSERVE_ORG

STREAMS = ["telemetry", "audit", "api-usage"]


async def ensure_streams() -> dict[str, bool]:
    """Verify streams exist. OpenObserve auto-creates on first ingest."""
    client = get_client()
    org = OPENOBSERVE_ORG
    results: dict[str, bool] = {}
    for stream in STREAMS:
        try:
            resp = await client.get(f"/api/{org}/{stream}")
            results[stream] = resp.status_code == 200
        except Exception:
            results[stream] = False
    return results


def stream_name(base: str) -> str:
    """Return today's stream name, e.g. cybersecsuite-telemetry-2026.04.18."""
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    return f"cybersecsuite-{base}-{today}"