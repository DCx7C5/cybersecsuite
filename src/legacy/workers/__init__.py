"""Worker API routes package — consolidated CRUD, lifecycle, metrics, history, and batch operations.

This package consolidates all worker-related routes under a single import point.

Modules:
    crud — Worker CRUD operations (POST, GET, PATCH, DELETE)
    lifecycle — Worker state transitions (start, stop, pause, resume, retry)
    metrics — Worker metrics, health, and audit logs
    history — Worker session history and bookmarks
    batch — Batch worker operations
"""

from .batch import batch_router