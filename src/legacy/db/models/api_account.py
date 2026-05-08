
from tortoise import fields
from css.core.db.models.base import BaseModel


class ApiAccount(BaseModel):
    """API account with vault-backed key, linked to ApiService."""

    vault_key = fields.CharField(max_length=255, pk=True)
    api_service = fields.ForeignKeyField(
        "models.ApiService", related_name="accounts", on_delete=fields.CASCADE
    )
    label = fields.CharField(max_length=255, null=True)
    active = fields.BooleanField(default=False)
    test_status = fields.CharField(max_length=20, null=True)
    last_tested_at = fields.DatetimeField(null=True)
    auth_method = fields.CharField(max_length=20, default="api_key")
    subject = fields.CharField(max_length=255, null=True)
    email = fields.CharField(max_length=255, null=True)
    display_name = fields.CharField(max_length=255, null=True)
    tenant = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "api_account"
        table_description_plural = "API Service Accounts"
        table_description_singular = "API Service Account"
        ordering = ["id"]
        ordering_field = "id"
        unique_together = (("api_service_id", "vault_key"),)
        indexes = [
            ("api_service_id", "active"),
        ]

