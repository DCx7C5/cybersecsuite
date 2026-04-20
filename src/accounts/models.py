"""Account entry Pydantic models."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AccountEntry(BaseModel):
    """Account metadata stored in vault (no secret material)."""

    vault_key: str = Field(description="Unique vault key name")
    provider_id: str = Field(description="Provider identifier (e.g., 'openai', 'anthropic')")
    label: str | None = Field(default=None, description="User-friendly label")
    active: bool = Field(default=False, description="Is this the active account for provider")
    auth_method: str = Field(default="api_key", description="Configured auth method")
    subject: str | None = Field(default=None, description="OAuth subject or upstream account id")
    email: str | None = Field(default=None, description="Associated email address")
    display_name: str | None = Field(default=None, description="Human-friendly account display name")
    tenant: str | None = Field(default=None, description="Optional tenant/org/workspace identifier")
    test_status: Literal["untested", "success", "failed"] | None = Field(
        default=None, description="Last test result"
    )
    last_tested_at: datetime | None = Field(default=None, description="Last test timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def _mask_key(key: str | None) -> str:
        """Mask API key for display, showing only last 4 chars."""
        if not key:
            return "****"
        if len(key) <= 4:
            return "****"
        return "****" + key[-4:]
