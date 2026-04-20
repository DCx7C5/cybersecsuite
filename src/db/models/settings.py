"""Settings and configuration storage models."""
from tortoise.models import Model
from tortoise import fields


class ScopedEntry(Model):
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


class GlobalSettings(Model):
    """Global application settings."""
    key = fields.CharField(max_length=128, primary_key=True)
    value = fields.JSONField(default=dict)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "global_settings"