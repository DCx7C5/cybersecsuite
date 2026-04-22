"""Core initial models — SharedEntry.

SharedEntry: general-purpose scoped key/value store.
"""
from tortoise import fields

from db.models.scope import ScopedEntry


class SharedEntry(ScopedEntry):
    """General-purpose scoped data store (findings, IOCs, risks are written here initially)."""
    id = fields.IntField(primary_key=True)
    value_type = fields.CharField(max_length=128, db_index=True)
    key = fields.CharField(max_length=512, default="")
    data = fields.JSONField(default=dict)

    class Meta:
        table = "shared_entries"

