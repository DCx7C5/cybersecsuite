"""
ApiService models — AI models available per API service and per API account.

Tables:
  api_service_models  — canonical model catalog per API service
  account_models      — per-account model access, tier overrides, rate limits
"""
from tortoise import fields
from tortoise.models import Model

from db.models.enums import ModelTier, ModelStatus


class ApiServiceModel(Model):
    """
    A single AI model offered by an API service.

    Populated via sync_pricing / live models API. One row per (api_service, model_id).
    Capability flags enable UI filtering and routing decisions.
    """

    id = fields.UUIDField(pk=True)
    api_service = fields.ForeignKeyField(
        "models.ApiService", related_name="models", on_delete=fields.CASCADE
    )

    # Identity
    model_id = fields.CharField(max_length=128)          # e.g. "claude-opus-4-5"
    display_name = fields.CharField(max_length=255)
    description = fields.TextField(default="")

    # Context / output limits
    context_window = fields.IntField(null=True)           # tokens
    max_output_tokens = fields.IntField(null=True)        # tokens

    # Pricing (per million tokens, USD)
    input_cost_per_mtok = fields.DecimalField(max_digits=14, decimal_places=6, null=True)
    output_cost_per_mtok = fields.DecimalField(max_digits=14, decimal_places=6, null=True)
    cache_read_cost_per_mtok = fields.DecimalField(max_digits=14, decimal_places=6, null=True)
    cache_write_cost_per_mtok = fields.DecimalField(max_digits=14, decimal_places=6, null=True)

    # Capabilities
    supports_vision = fields.BooleanField(default=False)
    supports_tools = fields.BooleanField(default=True)
    supports_streaming = fields.BooleanField(default=True)
    supports_thinking = fields.BooleanField(default=False)
    supports_prompt_cache = fields.BooleanField(default=False)
    supports_batches = fields.BooleanField(default=False)
    supports_computer_use = fields.BooleanField(default=False)
    supports_memory_tool = fields.BooleanField(default=False)

    # Modalities JSON list: ["text", "image", "audio", "video"]
    modalities = fields.JSONField(default=list)

    # Required beta headers to unlock capabilities (list of strings)
    required_betas = fields.JSONField(default=list)

    # Access tier
    tier = fields.CharEnumField(ModelTier, default=ModelTier.STANDARD)
    status = fields.CharEnumField(ModelStatus, default=ModelStatus.ACTIVE)

    # Lifecycle
    enabled = fields.BooleanField(default=True)
    deprecated_at = fields.DatetimeField(null=True)
    discovered_at = fields.DatetimeField(auto_now_add=True)
    last_seen_at = fields.DatetimeField(auto_now=True)

    # Raw extra metadata from API service
    extra = fields.JSONField(default=dict)

    class Meta:
        table = "api_service_models"
        unique_together = (("api_service_id", "model_id"),)
        ordering = ["api_service_id", "model_id"]

    def __str__(self) -> str:
        return f"ApiServiceModel({self.api_service_id}/{self.model_id})"


class AccountModel(Model):
    """
    Model access state for a specific API account.

    Not all accounts have access to all models (tiers, beta programs, etc.).
    This table holds the per-account override and the last verified accessibility.
    """

    id = fields.UUIDField(pk=True)
    account = fields.ForeignKeyField(
        "models.ApiAccount", related_name="account_models", on_delete=fields.CASCADE
    )
    api_service_model = fields.ForeignKeyField(
        "models.ApiServiceModel", related_name="account_access", on_delete=fields.CASCADE
    )

    # Access state
    accessible = fields.BooleanField(default=True)
    access_error = fields.CharField(max_length=512, null=True)   # last error if not accessible

    # Per-account tier override (e.g. account has enterprise but model is standard)
    tier_override = fields.CharEnumField(ModelTier, null=True)

    # Per-account rate limit overrides (null = use API service defaults)
    rate_limit_rpm = fields.IntField(null=True)
    rate_limit_tpm = fields.IntField(null=True)

    # When we last verified this account can actually call this model
    last_verified_at = fields.DatetimeField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "account_models"
        unique_together = (("account_id", "api_service_model_id"),)

    def __str__(self) -> str:
        return f"AccountModel({self.account_id} → {self.api_service_model_id})"
