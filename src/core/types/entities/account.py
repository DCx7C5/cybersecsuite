"""Account entity — represents external provider credentials and authentication state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .base import BaseEntity
from ..headers import BaseAccountHeader


@dataclass
class Account(BaseEntity):
    """Concrete account entity for external provider credentials.

    Represents an authenticated account/connection to an external provider
    (e.g., OpenAI, Anthropic, Vault service, etc.).

    The entity's id is the vault_key (registry key), and all other fields
    preserve AccountEntry fidelity for integration with credential stores.
    """

    header: BaseAccountHeader | None = None
    vault_key: str = ""
    provider_id: str = ""
    label: str = ""
    auth_method: str = "api_key"
    active: bool = False
    subject: str | None = None
    email: str | None = None
    display_name: str | None = None
    tenant: str | None = None
    test_status: str = "untested"
    last_tested_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Ensure vault_key mirrors id."""
        super().__post_init__()
        if self.vault_key and not self.id:
            self.id = self.vault_key
        elif self.id and not self.vault_key:
            self.vault_key = self.id

    @property
    def is_active(self) -> bool:
        """Check if this account is currently active."""
        return self.active and self.test_status == "passed"

    @property
    def needs_test(self) -> bool:
        """Check if this account needs credential verification."""
        return self.test_status in ("untested", "failed")

    def mark_tested(self, success: bool) -> None:
        """Mark this account as tested with result."""
        self.test_status = "passed" if success else "failed"
        self.last_tested_at = datetime.now()
