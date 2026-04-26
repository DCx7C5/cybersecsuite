"""Provider and auth method models - DB mirror of ProviderConfig registry."""
from tortoise import fields
from tortoise.models import Model


class Provider(Model):
    """AI provider configuration stored in DB."""
    id = fields.CharField(max_length=40, pk=True)
    name = fields.CharField(max_length=80)
    base_url = fields.CharField(max_length=255)
    auth_type = fields.CharField(max_length=12)
    auth_header = fields.CharField(max_length=20, default="Authorization")
    auth_prefix = fields.CharField(max_length=10, default="Bearer")
    api_format = fields.CharField(max_length=10, default="openai")
    env_key = fields.CharField(max_length=40)
    is_free = fields.BooleanField(default=False)
    enabled = fields.BooleanField(default=True)
    max_retries = fields.IntField(default=3)
    timeout_seconds = fields.IntField(default=60)
    rate_limit_rpm = fields.IntField(default=60)
    rate_limit_tpm = fields.IntField(default=1000000)
    extra = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "providers"

    def __str__(self):
        return f"Provider({self.id})"


class ProviderAuthMethod(Model):
    """M2M: Provider ↔ supported auth methods."""
    provider = fields.ForeignKeyField(
        "models.Provider", related_name="auth_methods", on_delete=fields.CASCADE
    )
    auth_method = fields.CharField(max_length=20)
    config = fields.JSONField(default=dict)
    auth_flow_id = fields.CharField(max_length=64, null=True)
    device_code = fields.CharField(max_length=255, null=True)
    user_code = fields.CharField(max_length=64, null=True)
    expires_at = fields.DatetimeField(null=True)
    last_polled_at = fields.DatetimeField(null=True)
    revoked_at = fields.DatetimeField(null=True)

    class Meta:
        table = "provider_auth_methods"
        unique_together = (("provider", "auth_method"),)
        indexes = (("provider_id", "revoked_at"),)

    def __str__(self):
        return f"ProviderAuthMethod({self.provider_id}, {self.auth_method})"
