"""Tests for crypto module — Ed25519 signing, BLAKE2b, Argon2id, AES-256-GCM."""

import json

import pytest

try:
    from crypto.key_manager import KeyManager, PasswordManager
    from crypto.artifact_manager import ArtifactManager
    from crypto.vault import CryptographicVault
    from crypto.config import get_crypto_config

    CRYPTO_AVAILABLE = True
except ImportError as e:
    CRYPTO_AVAILABLE = False
    pytest.skip(f"Crypto module not fully available: {e}", allow_module_level=True)


@pytest.fixture
def temp_key_dir(tmp_path):
    """Temporary key directory."""
    key_dir = tmp_path / "keys"
    key_dir.mkdir()
    return key_dir


@pytest.fixture
def temp_vault_dir(tmp_path):
    """Temporary vault directory."""
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    return vault_dir


class TestKeyManager:
    """Test Ed25519 key generation and management."""

    @pytest.mark.asyncio
    async def test_generate_keypair(self, temp_key_dir):
        """Test Ed25519 keypair generation."""
        km = KeyManager(key_dir=str(temp_key_dir))
        public_key, private_key_encrypted = await km.generate_keypair(
            name="test-key",
            password="strong_password_123!",
        )

        assert public_key
        assert private_key_encrypted
        assert len(public_key) == 32  # Ed25519 public key is 32 bytes
        assert (temp_key_dir / "test-key.pub").exists()
        assert (temp_key_dir / "test-key").exists()

    @pytest.mark.asyncio
    async def test_load_keypair(self, temp_key_dir):
        """Test loading a stored keypair."""
        km = KeyManager(key_dir=str(temp_key_dir))
        password = "test_password_456!"

        # Generate
        pub1, priv1 = await km.generate_keypair("test-key", password)

        # Load
        pub2, priv2 = await km.load_keypair("test-key", password)

        assert pub1 == pub2
        assert priv1 == priv2

    @pytest.mark.asyncio
    async def test_wrong_password_fails(self, temp_key_dir):
        """Test that wrong password fails to decrypt."""
        km = KeyManager(key_dir=str(temp_key_dir))
        await km.generate_keypair("test-key", "correct_password")

        with pytest.raises(Exception):  # Decryption should fail
            await km.load_keypair("test-key", "wrong_password")


class TestArtifactManager:
    """Test artifact signing and verification."""

    @pytest.mark.asyncio
    async def test_sign_and_verify_artifact(self, temp_key_dir):
        """Test signing and verifying an artifact."""
        km = KeyManager(key_dir=str(temp_key_dir))
        am = ArtifactManager(key_manager=km)

        password = "artifact_test_123!"
        pub_key, priv_key = await km.generate_keypair("artifact-signer", password)

        # Artifact payload
        payload = {
            "investigation_id": "INV-001",
            "findings": [
                {"type": "IOC", "value": "192.168.1.100"},
                {"type": "hash", "value": "abc123def456"},
            ],
            "timestamp": "2024-01-17T12:00:00Z",
        }
        payload_json = json.dumps(payload, sort_keys=True)

        # Sign
        signature = await am.sign_artifact(
            payload_json,
            key_name="artifact-signer",
            password=password,
        )
        assert signature
        assert len(signature) > 64  # Ed25519 sig + metadata

        # Verify
        is_valid = await am.verify_artifact(
            payload_json,
            signature,
            key_name="artifact-signer",
        )
        assert is_valid

    @pytest.mark.asyncio
    async def test_tampered_artifact_fails_verification(self, temp_key_dir):
        """Test that tampering with artifact invalidates signature."""
        km = KeyManager(key_dir=str(temp_key_dir))
        am = ArtifactManager(key_manager=km)

        password = "tamper_test!"
        await km.generate_keypair("tamper-signer", password)

        payload = '{"data": "original"}'
        signature = await am.sign_artifact(payload, "tamper-signer", password)

        # Tamper with payload
        tampered = '{"data": "modified"}'
        is_valid = await am.verify_artifact(tampered, signature, "tamper-signer")
        assert not is_valid


class TestPasswordManager:
    """Test password hashing (Argon2id)."""

    @pytest.mark.asyncio
    async def test_hash_and_verify_password(self):
        """Test Argon2id hashing and verification."""
        pm = PasswordManager()
        password = "complex_pwd_with_symbols!@#$%"

        # Hash
        hashed = await pm.hash_password(password)
        assert hashed
        assert hashed != password  # Not plaintext

        # Verify correct password
        assert await pm.verify_password(password, hashed)

        # Verify wrong password
        assert not await pm.verify_password("wrong_password", hashed)

    @pytest.mark.asyncio
    async def test_hash_consistency(self):
        """Test that hashing is consistent."""
        pm = PasswordManager()
        password = "test_password"

        hash1 = await pm.hash_password(password)
        hash2 = await pm.hash_password(password)

        # Hashes should differ (salt), but both verify
        assert hash1 != hash2
        assert await pm.verify_password(password, hash1)
        assert await pm.verify_password(password, hash2)


class TestCryptographicVault:
    """Test AES-256-GCM encrypted secret vault."""

    @pytest.mark.asyncio
    async def test_store_and_retrieve_secret(self, temp_vault_dir):
        """Test storing and retrieving encrypted secrets."""
        vault = CryptographicVault(vault_dir=str(temp_vault_dir))
        master_pass = "master_password_xyz!"

        # Store
        secret = "database_password_super_secret"
        await vault.store_secret(
            name="db-creds",
            secret=secret,
            master_password=master_pass,
        )

        # Retrieve
        retrieved = await vault.get_secret("db-creds", master_pass)
        assert retrieved == secret

    @pytest.mark.asyncio
    async def test_wrong_master_password_fails(self, temp_vault_dir):
        """Test that wrong master password fails to decrypt."""
        vault = CryptographicVault(vault_dir=str(temp_vault_dir))

        await vault.store_secret("secret1", "value1", "correct_pass")

        with pytest.raises(Exception):
            await vault.get_secret("secret1", "wrong_pass")

    @pytest.mark.asyncio
    async def test_list_secrets(self, temp_vault_dir):
        """Test listing all secrets in vault."""
        vault = CryptographicVault(vault_dir=str(temp_vault_dir))
        master_pass = "pass123"

        await vault.store_secret("secret1", "val1", master_pass)
        await vault.store_secret("secret2", "val2", master_pass)

        secrets = await vault.list_secrets()
        assert "secret1" in secrets
        assert "secret2" in secrets


class TestCryptoConfig:
    """Test crypto configuration."""

    def test_get_crypto_config(self):
        """Test reading crypto config."""
        config = get_crypto_config()
        assert config.algorithm == "Ed25519"
        assert config.hash_algorithm == "blake2b"
        assert config.hash_digest_size == 32
        assert config.argon2_memory == 262144
        assert config.argon2_iterations == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
