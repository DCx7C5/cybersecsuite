"""AccountManager singleton for API key management."""

from __future__ import annotations

import os
from typing import Any

from accounts.models import AccountEntry
from accounts.registry import get_registry
from crypto.vault import SecretNotFoundError, Vault


class AccountManager:
    """Singleton for managing API accounts with vault-backed keys."""

    _instance: "AccountManager | None" = None

    def __init__(self) -> None:
        self._vault: Vault | None = None
        self._env_mode: bool = False

    @classmethod
    def instance(cls) -> "AccountManager | None":
        """Get the singleton instance."""
        return cls._instance

    @classmethod
    def initialize(cls, vault_dir: str | None = None, env_only: bool = False) -> "AccountManager":
        """Initialize the AccountManager singleton."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._vault = Vault(vault_dir) if vault_dir else Vault()
            cls._instance._env_mode = env_only
        return cls._instance

    async def add(
        self,
        provider_id: str,
        api_key: str,
        label: str | None = None,
    ) -> AccountEntry:
        """Add a new API account."""
        vault_key = f"{provider_id}-{os.urandom(4).hex()}"
        if label is None:
            label = provider_id

        entry = AccountEntry(
            vault_key=vault_key,
            provider_id=provider_id,
            label=label,
            active=True,
        )

        self._vault.set_secret(vault_key, api_key)
        get_registry().add(entry)
        return entry

    async def rotate(self, vault_key: str, new_key: str) -> AccountEntry | None:
        """Rotate an existing account's key."""
        entry = get_registry().get(vault_key)
        if entry is None:
            return None

        self._vault.set_secret(vault_key, new_key)
        entry.updated_at = entry.updated_at.now()
        return entry

    async def delete(self, vault_key: str) -> bool:
        """Delete an account."""
        entry = get_registry().remove(vault_key)
        if entry is None:
            return False
        try:
            self._vault.delete_secret(vault_key)
        except SecretNotFoundError:
            pass
        return True

    async def list_all(self) -> list[AccountEntry]:
        """List all accounts."""
        return get_registry().list_all()

    async def set_active(self, vault_key: str) -> AccountEntry | None:
        """Set an account as active for its provider."""
        entry = get_registry().get(vault_key)
        if entry is None:
            return None

        for existing in get_registry().list_all():
            if existing.provider_id == entry.provider_id:
                existing.active = False

        entry.active = True
        get_registry().add(entry)
        return entry

    async def resolve(self, provider_id: str) -> str | None:
        """Resolve API key for a provider (vault first, then env var)."""
        entry = get_registry().get_by_provider(provider_id)
        if entry:
            try:
                return self._vault.get_secret(entry.vault_key)
            except SecretNotFoundError as e:
                raise e from e  # Don't mask real vault errors

        env_key = f"{provider_id.upper()}_API_KEY"
        return os.environ.get(env_key)

    async def test(self, vault_key: str) -> bool:
        """Test an account's key validity."""
        entry = get_registry().get(vault_key)
        if entry is None:
            return False

        try:
            key = self._vault.get_secret(vault_key)
            if not key:
                return False

            if entry.provider_id == "openai":
                import httpx

                resp = await httpx.AsyncClient().get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {key}"},
                    timeout=10.0,
                )
                entry.test_status = "success" if resp.status_code == 200 else "failed"

            elif entry.provider_id == "anthropic":
                import httpx

                resp = await httpx.AsyncClient().post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": key,
                        "anthropic-version": "2023-06-01",
                    },
                    json={"model": "claude-3-haiku-20240307", "max_tokens": 1},
                    timeout=10.0,
                )
                entry.test_status = "success" if resp.status_code == 200 else "failed"

            else:
                entry.test_status = "untested"

            return entry.test_status == "success"

        except Exception:
            entry.test_status = "failed"
            return False


_manager: AccountManager | None = None


def get_manager() -> AccountManager:
    """Get the global AccountManager instance."""
    global _manager
    if _manager is None:
        _manager = AccountManager.initialize()
    return _manager