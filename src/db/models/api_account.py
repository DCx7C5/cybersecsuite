from tortoise import fields
from tortoise.models import Model


class ApiAccount(Model):
    """API account with vault-backed key, linked to Provider."""

    vault_key = fields.CharField(max_length=255, pk=True)
    provider = fields.ForeignKeyField(
        "models.Provider", related_name="accounts", on_delete=fields.CASCADE
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

    def __init__(self, **kwargs: Any):
        super().__init__(kwargs)
        self.provider_id = None

    def __str__(self):
        return f"ApiAccount({self.vault_key})"