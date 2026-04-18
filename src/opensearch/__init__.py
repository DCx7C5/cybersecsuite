"""OpenSearch async client package for CyberSecSuite.

Exports:
  get_client()       — async OpenSearch singleton
  ensure_indices()   — create index templates on startup
  bulk_index()       — fire-and-forget bulk writer helper
  close_client()     — graceful shutdown
"""

from opensearch.client import close_client, get_client
from opensearch.indices import ensure_indices
from opensearch.writer import bulk_index

__all__ = ["get_client", "close_client", "ensure_indices", "bulk_index"]
