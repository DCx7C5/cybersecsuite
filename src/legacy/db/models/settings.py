"""Settings and configuration storage models."""
from css.core.db.models.base import BaseModel
from tortoise import fields


class ScopedEntry(BaseModel):
    """Key-value store for project/app-scoped settings."""
    entry_type = fields.CharField(max_length=64, db_index=True)
    project = fields.ForeignKeyField("models.Project", related_name=False, null=True, on_delete=fields.CASCADE, db_index=True)
    session = fields.ForeignKeyField("models.Session", related_name=False, null=True, on_delete=fields.CASCADE)
    data = fields.JSONField(default=dict)
    is_active = fields.BooleanField(default=True, db_index=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "scoped_entries"


class GlobalSettings(BaseModel):
    """Global application settings."""
    key = fields.CharField(max_length=128, primary_key=True)
    value = fields.JSONField(default=dict)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "global_settings"