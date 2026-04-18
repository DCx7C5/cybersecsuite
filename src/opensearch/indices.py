"""Index template creation for CyberSecSuite OpenSearch indices."""

from __future__ import annotations

from opensearch.client import get_client

# Index prefix for all managed indices
INDEX_PREFIX = "cybersecsuite"

_COMMON_SETTINGS = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "refresh_interval": "5s",
}

_TEMPLATES = [
    {
        "name": f"{INDEX_PREFIX}-telemetry",
        "pattern": f"{INDEX_PREFIX}-telemetry-*",
        "mappings": {
            "properties": {
                "@timestamp":  {"type": "date"},
                "metric_name": {"type": "keyword"},
                "value_ms":    {"type": "float"},
                "method":      {"type": "keyword"},
                "status":      {"type": "keyword"},
                "path":        {"type": "keyword"},
            }
        },
    },
    {
        "name": f"{INDEX_PREFIX}-audit",
        "pattern": f"{INDEX_PREFIX}-audit-*",
        "mappings": {
            "properties": {
                "@timestamp":  {"type": "date"},
                "action":      {"type": "keyword"},
                "entity_type": {"type": "keyword"},
                "entity_id":   {"type": "keyword"},
                "agent":       {"type": "keyword"},
                "resource":    {"type": "keyword"},
                "ip_address":  {"type": "ip", "ignore_malformed": True},
                "detail":      {"type": "text"},
            }
        },
    },
    {
        "name": f"{INDEX_PREFIX}-api-usage",
        "pattern": f"{INDEX_PREFIX}-api-usage-*",
        "mappings": {
            "properties": {
                "@timestamp":  {"type": "date"},
                "provider":    {"type": "keyword"},
                "model":       {"type": "keyword"},
                "tokens_in":   {"type": "long"},
                "tokens_out":  {"type": "long"},
                "cost_usd":    {"type": "float"},
                "duration_ms": {"type": "float"},
                "strategy":    {"type": "keyword"},
            }
        },
    },
]


async def ensure_indices() -> None:
    """Create index templates (idempotent). Call once during app lifespan startup."""
    client = get_client()
    for tpl in _TEMPLATES:
        body = {
            "index_patterns": [tpl["pattern"]],
            "template": {
                "settings": _COMMON_SETTINGS,
                "mappings": tpl["mappings"],
            },
        }
        try:
            await client.indices.put_index_template(name=tpl["name"], body=body)
        except Exception:
            # Non-fatal — templates are best-effort on startup
            pass


def daily_index(base: str) -> str:
    """Return today's daily rollover index name, e.g. cybersecsuite-telemetry-2026.04.18."""
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    return f"{INDEX_PREFIX}-{base}-{today}"
