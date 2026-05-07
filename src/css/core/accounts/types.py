"""Account entity for core/accounts."""

import msgspec
from datetime import datetime
from typing import Any

from css.core.types.base_entity import BaseEntity
from css.core.types.base_headers import BaseAccountHeader


class Account(BaseEntity):
    """Credential and authentication entity for an external provider.

    Stores vault key, auth method, and test state for one provider account.
    """

    header: BaseAccountHeader | None = None
    vault_key: str = ""
    provider_id: str = ""
    label: str = ""
    auth_method: str = "api_key"
    active: bool = False
    last_tested_at: datetime | None = None
    test_failed: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()

    @property
    def is_active(self) -> bool:
        """Account is enabled and has a vault key."""
        return self.active and bool(self.vault_key)

    @property
    def needs_test(self) -> bool:
        """Account has never been tested or last test failed."""
        return self.last_tested_at is None or self.test_failed

    def mark_tested(self, *, success: bool) -> None:
        """Record test result."""
        self.last_tested_at = datetime.utcnow()
        self.test_failed = not success

    def to_dict(self) -> dict[str, Any]:
        return msgspec.to_builtin(self)  # type: ignore[no-any-return]


__all__ = ["Account"]
