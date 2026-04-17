"""
File-based secret vault with Argon2id + AES-256-GCM encryption.

Stores encrypted secrets (passfiles) in ``~/.dystopian-crypto/vault/``.
Each secret is a single ``{name}.enc`` file whose plaintext is protected
by a master password read from a file — identical to the scheme used by
:class:`crypto.key_manager.PasswordManager`.
"""
import os
from pathlib import Path

from crypto.key_manager import PasswordManager


_DEFAULT_VAULT_DIR = str(Path.home() / ".dystopian-crypto" / "vault")


class VaultError(Exception):
    """Base exception for vault operations."""


class SecretNotFoundError(VaultError):
    """Raised when a requested secret does not exist."""


class SecretExistsError(VaultError):
    """Raised when storing a secret that already exists."""


class Vault:
    """Simple file-based secret vault.

    Secrets are encrypted with a master password via
    :class:`crypto.key_manager.PasswordManager` (Argon2id KDF →
    AES-256-GCM) and stored as individual ``.enc`` files under the
    vault directory.

    Args:
        vault_dir: Filesystem path for the vault.  Defaults to
            ``~/.dystopian-crypto/vault/``.
    """

    _ENC_SUFFIX = ".enc"

    def __init__(self, vault_dir: str | None = None) -> None:
        self.vault_dir = Path(vault_dir or _DEFAULT_VAULT_DIR)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        # Vault directory must be owner-only accessible.
        os.chmod(self.vault_dir, 0o700)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _secret_path(self, name: str) -> Path:
        """Return the on-disk path for a named secret."""
        _validate_name(name)
        return self.vault_dir / f"{name}{self._ENC_SUFFIX}"

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def store(
        self,
        name: str,
        content: str,
        master_password_file: str,
        *,
        overwrite: bool = False,
    ) -> Path:
        """Encrypt *content* and write it to the vault.

        Args:
            name: Logical secret name (alphanumeric + hyphens/underscores).
            content: The plaintext secret to store.
            master_password_file: Path to a file containing the master
                password (read and stripped).
            overwrite: If ``True``, silently replace an existing secret.

        Returns:
            The :class:`~pathlib.Path` of the written ``.enc`` file.

        Raises:
            SecretExistsError: If the secret already exists and
                *overwrite* is ``False``.
            FileNotFoundError: If *master_password_file* does not exist.
        """
        dest = self._secret_path(name)

        if dest.exists() and not overwrite:
            raise SecretExistsError(
                f"Secret '{name}' already exists. Use overwrite=True to replace."
            )

        _validate_password_file(master_password_file)

        encrypted = PasswordManager.encrypt_key(
            content.encode("utf-8"), master_password_file
        )
        dest.write_bytes(encrypted)
        os.chmod(dest, 0o600)
        return dest

    def retrieve(self, name: str, master_password_file: str) -> str:
        """Decrypt and return a stored secret.

        Args:
            name: Logical secret name.
            master_password_file: Path to a file containing the master
                password.

        Returns:
            The decrypted plaintext as a string.

        Raises:
            SecretNotFoundError: If no secret with *name* exists.
            FileNotFoundError: If *master_password_file* does not exist.
            cryptography.exceptions.InvalidTag: If the master password is
                wrong (authentication failure).
        """
        src = self._secret_path(name)
        if not src.exists():
            raise SecretNotFoundError(f"Secret '{name}' not found in vault.")

        _validate_password_file(master_password_file)

        encrypted = src.read_bytes()
        plaintext = PasswordManager.decrypt_key(encrypted, master_password_file)
        return plaintext.decode("utf-8")

    def list_secrets(self) -> list[str]:
        """Return sorted names of all secrets in the vault.

        Returns:
            A list of secret names (without the ``.enc`` extension).
        """
        names: list[str] = []
        for path in sorted(self.vault_dir.glob(f"*{self._ENC_SUFFIX}")):
            if path.is_file():
                names.append(path.stem)
        return names

    def delete(self, name: str) -> bool:
        """Remove a secret from the vault.

        Args:
            name: Logical secret name.

        Returns:
            ``True`` if the secret was deleted, ``False`` if it did not
            exist.
        """
        target = self._secret_path(name)
        if target.exists():
            target.unlink()
            return True
        return False

    def exists(self, name: str) -> bool:
        """Check whether a named secret exists.

        Args:
            name: Logical secret name.

        Returns:
            ``True`` if the secret is present on disk.
        """
        return self._secret_path(name).exists()

    # ------------------------------------------------------------------
    # dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Vault(vault_dir={str(self.vault_dir)!r})"


# ------------------------------------------------------------------
# module-level helpers
# ------------------------------------------------------------------

def _validate_name(name: str) -> None:
    """Ensure *name* is safe for use as a filename component."""
    if not name:
        raise ValueError("Secret name must not be empty.")
    # Allow alphanumeric, hyphens, underscores, dots — no path separators.
    for ch in name:
        if not (ch.isalnum() or ch in "-_."):
            raise ValueError(
                f"Invalid character {ch!r} in secret name '{name}'. "
                "Use alphanumeric characters, hyphens, underscores, or dots."
            )


def _validate_password_file(path: str) -> None:
    """Raise :class:`FileNotFoundError` if *path* does not exist."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Master password file not found: {path}")
