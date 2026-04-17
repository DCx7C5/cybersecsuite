"""
Audit log — re-exports AuditLog from core to avoid import breakage.
The canonical AuditLog model lives in db.models.core.
"""
from db.models.core import AuditLog  # noqa: F401 — canonical model in core.py

__all__ = ["AuditLog"]
