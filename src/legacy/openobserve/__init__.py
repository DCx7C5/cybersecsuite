"""OpenObserve async client package for CyberSecSuite.

Exports:
  get_client()       — async httpx client singleton
  ensure_streams()   — verify/recommend streams on startup
  bulk_index()       — fire-and-forget bulk writer helper
  close_client()    — graceful shutdown
  getLogger          — module-level logger
"""
from legacy.logger import getLogger

from openobserve.client import close_client, get_client
from openobserve.streams import ensure_streams
from openobserve.writer import bulk_index

__all__ = ["get_client", "close_client", "ensure_streams", "bulk_index", "getLogger"]