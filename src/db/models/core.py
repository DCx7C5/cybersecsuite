"""Core initial models — SharedEntry.

SharedEntry: general-purpose scoped key/value store.
"""
from tortoise import fields

from db.models.scope import ScopedEntry


class SharedEntry(ScopedEntry):
    """General-purpose scoped data store (findings, IOCs, risks are written here initially)."""
    id = fields.BigIntField(primary_key=True)
    value_type = fields.CharField(max_length=128, db_index=True)
    key = fields.CharField(max_length=512, default="")
    data = fields.JSONField(default=dict)

    class Meta:
        table = "shared_entries"


class AuditLog(ScopedEntry):
    """Audit trail for all scope-level operations.
    
    Tracks user actions, resource accesses, and security events
    with full scope hierarchy support.
    """
    id = fields.BigIntField(primary_key=True)
    user_id = fields.CharField(max_length=128, index=True)
    resource = fields.CharField(max_length=256, index=True)
    action = fields.CharField(max_length=64)
    scope_level = fields.CharField(max_length=16)
    result = fields.CharField(max_length=32)
    details = fields.JSONField(default=dict)
    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "audit_logs"
        indexes = [
            ("user_id", "timestamp"),
            ("resource", "action"),
            ("scope_level", "timestamp"),
        ]
