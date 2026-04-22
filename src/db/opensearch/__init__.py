"""OpenSearch support package for CyberSecSuite."""
from db.opensearch.mappings import (
    ALL_INDICES,
    FINDINGS_MAPPING,
    IOCS_MAPPING,
    AUDIT_LOGS_MAPPING,
    ensure_indices,
    sync_finding,
    sync_ioc,
    sync_audit_log,
)

__all__ = [
    "ALL_INDICES",
    "FINDINGS_MAPPING",
    "IOCS_MAPPING",
    "AUDIT_LOGS_MAPPING",
    "ensure_indices",
    "sync_finding",
    "sync_ioc",
    "sync_audit_log",
]
