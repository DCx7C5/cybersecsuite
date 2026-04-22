"""In-memory registry for account index, synced with vault + DB."""


from accounts.models import AccountEntry


class AccountRegistry:
    """In-memory index of accounts, synced with vault and DB."""

    def __init__(self) -> None:
        self._by_vault_key: dict[str, AccountEntry] = {}
        self._by_provider: dict[str, str] = {}  # provider_id -> vault_key

    def add(self, entry: AccountEntry) -> None:
        """Add or update an account entry."""
        self._by_vault_key[entry.vault_key] = entry
        if entry.active:
            self._by_provider[entry.provider_id] = entry.vault_key

    def get(self, vault_key: str) -> AccountEntry | None:
        """Get entry by vault key."""
        return self._by_vault_key.get(vault_key)

    def get_by_provider(self, provider_id: str) -> AccountEntry | None:
        """Get active account for a provider."""
        vault_key = self._by_provider.get(provider_id)
        if vault_key:
            return self._by_vault_key.get(vault_key)
        return None

    def list_all(self) -> list[AccountEntry]:
        """List all accounts."""
        return list(self._by_vault_key.values())

    def remove(self, vault_key: str) -> AccountEntry | None:
        """Remove an account by vault key."""
        entry = self._by_vault_key.pop(vault_key, None)
        if entry and entry.provider_id in self._by_provider:
            del self._by_provider[entry.provider_id]
        return entry

    def clear(self) -> None:
        """Clear all entries."""
        self._by_vault_key.clear()
        self._by_provider.clear()


_registry: AccountRegistry | None = None


def get_registry() -> AccountRegistry:
    """Get the global account registry."""
    global _registry
    if _registry is None:
        _registry = AccountRegistry()
    return _registry