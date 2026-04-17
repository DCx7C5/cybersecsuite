"""
Audit log — immutable record of every significant action.
"""
from tortoise.models import Model
from tortoise import fields

from db.models.enums import AuditAction


class AuditLog(Model):
    """Immutable audit trail entry."""
    id = fields.IntField(primary_key=True)
    action = fields.CharEnumField(AuditAction, db_index=True)
    entity_type = fields.CharField(max_length=128, db_index=True, default="")
    entity_id = fields.IntField(db_index=True, null=True)
    entity_repr = fields.CharField(max_length=512, default="")
    workspace = fields.ForeignKeyField("models.Workspace", related_name="audit_logs", null=True, on_delete=fields.SET_NULL)
    session = fields.ForeignKeyField("models.Session", related_name="audit_logs", null=True, on_delete=fields.SET_NULL)
    agent = fields.CharField(max_length=256, db_index=True)
    resource = fields.CharField(max_length=1024, default="", db_index=True)
    ip_address = fields.CharField(max_length=45, default="")
    old_value = fields.JSONField(null=True)
    new_value = fields.JSONField(null=True)
    metadata = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            ("entity_type", "entity_id"),
            ("workspace", "created_at"),
            ("agent", "created_at"),
            ("action", "entity_type"),
        ]
