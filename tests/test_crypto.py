"""Tests for crypto module — Ed25519 signing, BLAKE2b, Argon2id, AES-256-GCM."""

import pytest

try:
    from crypto.key_manager import KeyManager, PasswordManager
    from crypto.artifact_manager import ArtifactManager
    from crypto.vault import Vault
    from crypto.config import get_settings

    CRYPTO_AVAILABLE = True
except ImportError as e:
    CRYPTO_AVAILABLE = False
    pytest.skip(f"Crypto module not fully available: {e}", allow_module_level=True)


@pytest.fixture
def temp_key_dir(tmp_path):
    key_dir = tmp_path / "keys"
    key_dir.mkdir()
    return key_dir


@pytest.fixture
def temp_vault_dir(tmp_path):
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    return vault_dir


class TestKeyManager:
    """Test Ed25519 key generation and management."""

    def test_key_manager_init(self, temp_key_dir):
        km = KeyManager(keys_dir=str(temp_key_dir))
        assert km is not None

    def test_list_keys_empty(self, temp_key_dir):
        km = KeyManager(keys_dir=str(temp_key_dir))
        keys = km.list_keys()
        assert isinstance(keys, dict)
        assert len(keys) == 0


class TestPasswordManager:
    """Test password-based key encryption (Argon2id + AES-256-GCM)."""

    def test_encrypt_decrypt_roundtrip(self, tmp_path):
        password_file = tmp_path / "pass.txt"
        password_file.write_text("strong_password_123!")

        original = b"secret key material here"
        encrypted = PasswordManager.encrypt_key(original, str(password_file))
        assert encrypted != original

        decrypted = PasswordManager.decrypt_key(encrypted, str(password_file))
        assert decrypted == original

    def test_wrong_password_fails(self, tmp_path):
        correct_pass = tmp_path / "correct.txt"
        correct_pass.write_text("correct_password")
        wrong_pass = tmp_path / "wrong.txt"
        wrong_pass.write_text("wrong_password")

        original = b"some secret data"
        encrypted = PasswordManager.encrypt_key(original, str(correct_pass))

        with pytest.raises(Exception):
            PasswordManager.decrypt_key(encrypted, str(wrong_pass))


class TestVault:
    """Test AES-256-GCM encrypted secret vault."""

    def test_store_and_retrieve(self, temp_vault_dir, tmp_path):
        vault = Vault(vault_dir=str(temp_vault_dir))
        pass_file = tmp_path / "master.txt"
        pass_file.write_text("master_password_xyz!")

        vault.store("db-creds", "super_secret_value", str(pass_file))
        retrieved = vault.retrieve("db-creds", str(pass_file))
        assert retrieved == "super_secret_value"

    def test_list_secrets(self, temp_vault_dir, tmp_path):
        vault = Vault(vault_dir=str(temp_vault_dir))
        pass_file = tmp_path / "master.txt"
        pass_file.write_text("pass123")

        vault.store("secret1", "val1", str(pass_file))
        vault.store("secret2", "val2", str(pass_file))

        secrets = vault.list_secrets()
        assert "secret1" in secrets
        assert "secret2" in secrets

    def test_exists(self, temp_vault_dir, tmp_path):
        vault = Vault(vault_dir=str(temp_vault_dir))
        pass_file = tmp_path / "master.txt"
        pass_file.write_text("pass")

        assert not vault.exists("nonexistent")
        vault.store("exists-test", "val", str(pass_file))
        assert vault.exists("exists-test")

    def test_delete(self, temp_vault_dir, tmp_path):
        vault = Vault(vault_dir=str(temp_vault_dir))
        pass_file = tmp_path / "master.txt"
        pass_file.write_text("pass")

        vault.store("to-delete", "val", str(pass_file))
        assert vault.exists("to-delete")
        vault.delete("to-delete")
        assert not vault.exists("to-delete")


class TestCryptoConfig:
    """Test crypto configuration."""

    def test_get_settings(self):
        settings = get_settings()
        assert settings.crypto.algorithm == "Ed25519"
        assert settings.crypto.hash == "blake2b"
        assert settings.crypto.hash_digest_size == 32

    def test_argon2_params(self):
        settings = get_settings()
        kd = settings.crypto.key_derivation
        assert kd.memory_cost == 262144
        assert kd.iterations == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
