"""OpenSearch index definitions and sync helpers for CyberSecSuite.

Postgres remains the authoritative store. OpenSearch is a secondary index for
full-text search on high-volume tables. Never delete Postgres rows — only mirror.

Usage:
    from db.opensearch.mappings import FINDINGS_MAPPING, sync_finding

Plan ref: T047
"""
from __future__ import annotations

from typing import Any, Final

# ---------------------------------------------------------------------------
# Index settings (shared across all indices)
# ---------------------------------------------------------------------------
_SETTINGS: Final[dict[str, Any]] = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "refresh_interval": "5s",
}

# ---------------------------------------------------------------------------
# findings index
# ---------------------------------------------------------------------------
FINDINGS_MAPPING: Final[dict[str, Any]] = {
    "settings": _SETTINGS,
    "mappings": {
        "properties": {
            "id":            {"type": "keyword"},
            "title":         {"type": "text",    "analyzer": "standard", "fields": {"keyword": {"type": "keyword"}}},
            "description":   {"type": "text",    "analyzer": "standard"},
            "severity":      {"type": "keyword"},
            "category":      {"type": "keyword"},
            "status":        {"type": "keyword"},
            "cve_id":        {"type": "keyword"},
            "cvss_score":    {"type": "float"},
            "project_id":    {"type": "keyword"},
            "session_id":    {"type": "keyword"},
            "runtime_id":    {"type": "keyword"},
            "worktree_path": {"type": "keyword"},
            "scope_level":   {"type": "keyword"},
            "created_at":    {"type": "date"},
            "updated_at":    {"type": "date"},
            "is_active":     {"type": "boolean"},
        }
    },
}

# ---------------------------------------------------------------------------
# iocs index
# ---------------------------------------------------------------------------
IOCS_MAPPING: Final[dict[str, Any]] = {
    "settings": _SETTINGS,
    "mappings": {
        "properties": {
            "id":            {"type": "keyword"},
            "ioc_type":      {"type": "keyword"},
            "value":         {"type": "keyword", "fields": {"text": {"type": "text"}}},
            "description":   {"type": "text"},
            "confidence":    {"type": "float"},
            "severity":      {"type": "keyword"},
            "tags":          {"type": "keyword"},
            "source":        {"type": "keyword"},
            "tlp":           {"type": "keyword"},
            "project_id":    {"type": "keyword"},
            "session_id":    {"type": "keyword"},
            "runtime_id":    {"type": "keyword"},
            "worktree_path": {"type": "keyword"},
            "scope_level":   {"type": "keyword"},
            "first_seen":    {"type": "date"},
            "last_seen":     {"type": "date"},
            "created_at":    {"type": "date"},
            "is_active":     {"type": "boolean"},
        }
    },
}

# ---------------------------------------------------------------------------
# audit_logs index
# ---------------------------------------------------------------------------
AUDIT_LOGS_MAPPING: Final[dict[str, Any]] = {
    "settings": {**_SETTINGS, "refresh_interval": "1s"},
    "mappings": {
        "properties": {
            "id":          {"type": "keyword"},
            "action":      {"type": "keyword"},
            "actor":       {"type": "keyword"},
            "resource":    {"type": "keyword"},
            "resource_id": {"type": "keyword"},
            "detail":      {"type": "text"},
            "ip_address":  {"type": "ip"},
            "session_id":  {"type": "keyword"},
            "project_id":  {"type": "keyword"},
            "scope_level": {"type": "keyword"},
            "created_at":  {"type": "date"},
        }
    },
}

# ---------------------------------------------------------------------------
# Convenience: all index definitions keyed by canonical index name
# ---------------------------------------------------------------------------
ALL_INDICES: Final[dict[str, dict[str, Any]]] = {
    "cybersec-findings":   FINDINGS_MAPPING,
    "cybersec-iocs":       IOCS_MAPPING,
    "cybersec-audit-logs": AUDIT_LOGS_MAPPING,
}

# ---------------------------------------------------------------------------
# OpenSearch client helper (lazy import — opensearch-py is optional)
# ---------------------------------------------------------------------------

def _client(host: str = "localhost", port: int = 9200):
    """Return an OpenSearch client. Raises ImportError if not installed."""
    try:
        from opensearchpy import OpenSearch  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "opensearch-py is not installed. "
            "Run: uv add opensearch-py"
        ) from exc
    return OpenSearch([{"host": host, "port": port}])


def ensure_indices(host: str = "localhost", port: int = 9200) -> None:
    """Create all indices if they do not exist."""
    client = _client(host, port)
    for index, body in ALL_INDICES.items():
        if not client.indices.exists(index=index):
            client.indices.create(index=index, body=body)


def sync_finding(finding_dict: dict[str, Any], host: str = "localhost", port: int = 9200) -> None:
    """Mirror a single finding dict to OpenSearch."""
    client = _client(host, port)
    client.index(index="cybersec-findings", id=finding_dict["id"], body=finding_dict)


def sync_ioc(ioc_dict: dict[str, Any], host: str = "localhost", port: int = 9200) -> None:
    """Mirror a single IOC dict to OpenSearch."""
    client = _client(host, port)
    client.index(index="cybersec-iocs", id=ioc_dict["id"], body=ioc_dict)


def sync_audit_log(log_dict: dict[str, Any], host: str = "localhost", port: int = 9200) -> None:
    """Mirror a single audit log entry to OpenSearch."""
    client = _client(host, port)
    client.index(index="cybersec-audit-logs", id=log_dict["id"], body=log_dict)
