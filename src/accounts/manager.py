"""AccountManager singleton for persisted provider/account credential management."""
import json
import os
from typing import Any

from accounts.models import AccountEntry
from src.registries.accounts import get_registry
from crypto.vault import SecretNotFoundError, Vault


class AccountManager:
    """Singleton for managing provider accounts with vault-backed secrets."""

    _instance: AccountManager | None = None

    def __init__(self) -> None:
        self._vault: Vault | None = None
        self._env_mode: bool = False

    @classmethod
    def instance(cls) -> AccountManager | None:
        return cls._instance

    @classmethod
    def initialize(cls, vault_dir: str | None = None, env_only: bool = False) -> AccountManager | None:
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._vault = Vault(vault_dir) if vault_dir else Vault()
            cls._instance._env_mode = env_only
        return cls._instance

    async def _sync_registry_from_db(self) -> list[AccountEntry]:
        from db.models.api_account import ApiAccount

        rows = await ApiAccount.all().order_by("provider_id", "vault_key")
        registry = get_registry()
        registry.clear()

        entries: list[AccountEntry] = []
        for row in rows:
            entry = AccountEntry(
                vault_key=row.vault_key,
                provider_id=row.provider_id,
                label=row.label,
                active=row.active,
                auth_method=row.auth_method,
                subject=row.subject,
                email=row.email,
                display_name=row.display_name,
                tenant=row.tenant,
                test_status=row.test_status,
                last_tested_at=row.last_tested_at,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            registry.add(entry)
            entries.append(entry)
        return entries

    @staticmethod
    def _serialize_secret(secret: str | dict[str, Any]) -> str:
        if isinstance(secret, str):
            return secret
        return json.dumps(secret, separators=(",", ":"), sort_keys=True)

    @staticmethod
    def _deserialize_secret(raw_secret: str) -> str | dict[str, Any]:
        try:
            parsed = json.loads(raw_secret)
        except (TypeError, json.JSONDecodeError):
            return raw_secret
        return parsed if isinstance(parsed, dict) else raw_secret

    async def add(
        self,
        provider_id: str,
        secret: str | dict[str, Any],
        label: str | None = None,
        *,
        auth_method: str = "api_key",
        display_name: str | None = None,
        subject: str | None = None,
        email: str | None = None,
        tenant: str | None = None,
    ) -> AccountEntry:
        from db.models.api_account import ApiAccount

        vault_key = f"{provider_id}-{os.urandom(4).hex()}"
        if label is None:
            label = provider_id

        payload = self._serialize_secret(secret)
        self._vault.set_secret(vault_key, payload)

        await ApiAccount.create(
            vault_key=vault_key,
            provider_id=provider_id,
            label=label,
            active=True,
            auth_method=auth_method,
            subject=subject,
            email=email,
            display_name=display_name,
            tenant=tenant,
            test_status="untested",
        )

        for existing in await ApiAccount.filter(provider_id=provider_id).exclude(vault_key=vault_key):
            if existing.active:
                existing.active = False
                await existing.save(update_fields=["active", "updated_at"])

        entries = await self._sync_registry_from_db()
        return next(entry for entry in entries if entry.vault_key == vault_key)

    async def rotate(self, vault_key: str, new_secret: str | dict[str, Any]) -> AccountEntry | None:
        from db.models.api_account import ApiAccount

        row = await ApiAccount.get_or_none(vault_key=vault_key)
        if row is None:
            return None

        self._vault.set_secret(vault_key, self._serialize_secret(new_secret), overwrite=True)
        await row.save(update_fields=["updated_at"])

        entries = await self._sync_registry_from_db()
        return next((entry for entry in entries if entry.vault_key == vault_key), None)

    async def delete(self, vault_key: str) -> bool:
        from db.models.api_account import ApiAccount

        row = await ApiAccount.get_or_none(vault_key=vault_key)
        if row is None:
            return False

        await row.delete()
        try:
            self._vault.delete_secret(vault_key)
        except SecretNotFoundError:
            pass

        await self._sync_registry_from_db()
        return True

    async def list_all(self) -> list[AccountEntry]:
        return await self._sync_registry_from_db()

    async def set_active(self, vault_key: str) -> AccountEntry | None:
        from db.models.api_account import ApiAccount

        row = await ApiAccount.get_or_none(vault_key=vault_key)
        if row is None:
            return None

        await ApiAccount.filter(provider_id=row.provider_id).update(active=False)
        row.active = True
        await row.save(update_fields=["active", "updated_at"])

        entries = await self._sync_registry_from_db()
        return next((entry for entry in entries if entry.vault_key == vault_key), None)

    async def resolve(self, provider_id: str) -> str | None:
        await self._sync_registry_from_db()
        entry = get_registry().get_by_provider(provider_id)
        if entry:
            return self._vault.get_secret(entry.vault_key)

        env_key = f"{provider_id.upper().replace('-', '_')}_API_KEY"
        return os.environ.get(env_key)

    async def resolve_credentials(self, provider_id: str) -> dict[str, Any] | None:
        await self._sync_registry_from_db()
        entry = get_registry().get_by_provider(provider_id)
        if entry is None:
            return None

        raw_secret = self._vault.get_secret(entry.vault_key)
        secret = self._deserialize_secret(raw_secret)
        if isinstance(secret, dict):
            return secret
        return {"value": secret}

    async def test(self, vault_key: str) -> bool:
        from db.models.api_account import ApiAccount

        row = await ApiAccount.get_or_none(vault_key=vault_key)
        if row is None:
            return False

        try:
            secret = self._deserialize_secret(self._vault.get_secret(vault_key))
            status = "untested"

            if row.auth_method == "api_key" and isinstance(secret, str):
                if row.provider_id == "openai":
                    import httpx

                    resp = await httpx.AsyncClient().get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {secret}"},
                        timeout=10.0,
                    )
                    status = "success" if resp.status_code == 200 else "failed"
                elif row.provider_id == "anthropic":
                    import httpx

                    resp = await httpx.AsyncClient().post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": secret,
                            "anthropic-version": "2023-06-01",
                        },
                        json={"model": "claude-3-haiku-20240307", "max_tokens": 1, "messages": [{"role": "user", "content": "ping"}]},
                        timeout=10.0,
                    )
                    status = "success" if resp.status_code in {200, 400} else "failed"
            else:
                status = "untested"

            row.test_status = status
            await row.save(update_fields=["test_status", "updated_at"])
            await self._sync_registry_from_db()
            return status == "success"
        except Exception:
            row.test_status = "failed"
            await row.save(update_fields=["test_status", "updated_at"])
            await self._sync_registry_from_db()
            return False


_manager: AccountManager | None = None


def get_manager() -> AccountManager:
    """Get the global AccountManager instance."""
    global _manager
    if _manager is None:
        _manager = AccountManager.initialize()
    return _manager
