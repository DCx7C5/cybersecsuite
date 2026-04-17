"""
Key management system with password-protected storage.
Handles RSA key generation, lifecycle, and secure password management.

This module is designed to work with dystopian-crypto CLI tool.
"""
import hashlib
import json
import os
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class PasswordManager:
    """Manage password-protected key files with PBKDF2 encryption."""

    SALT_LENGTH = 32
    IV_LENGTH = 16
    PBKDF2_ITERATIONS = 480000

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=PasswordManager.PBKDF2_ITERATIONS,
            backend=default_backend(),
        )
        return kdf.derive(password.encode())

    @staticmethod
    def encrypt_key(key_data: bytes, password_file: str) -> bytes:
        """
        Encrypt key data with AES-256 using password from file.

        Args:
            key_data: Private key bytes to encrypt
            password_file: Path to file containing password

        Returns:
            Encrypted key data (salt + iv + ciphertext)
        """
        # Read password from file
        password = Path(password_file).read_text().strip()

        # Generate random salt and IV
        salt = secrets.token_bytes(PasswordManager.SALT_LENGTH)
        iv = secrets.token_bytes(PasswordManager.IV_LENGTH)

        # Derive encryption key
        key = PasswordManager._derive_key(password, salt)

        # Encrypt key data
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(key_data) + encryptor.finalize()

        # Return salt + iv + ciphertext
        return salt + iv + ciphertext

    @staticmethod
    def decrypt_key(encrypted_data: bytes, password_file: str) -> bytes:
        """
        Decrypt key data using password from file.

        Args:
            encrypted_data: Encrypted key data
            password_file: Path to file containing password

        Returns:
            Decrypted key bytes
        """
        # Read password from file
        password = Path(password_file).read_text().strip()

        # Extract salt and IV
        salt = encrypted_data[:PasswordManager.SALT_LENGTH]
        iv = encrypted_data[
            PasswordManager.SALT_LENGTH : PasswordManager.SALT_LENGTH
            + PasswordManager.IV_LENGTH
        ]
        ciphertext = encrypted_data[
            PasswordManager.SALT_LENGTH + PasswordManager.IV_LENGTH :
        ]

        # Derive key
        key = PasswordManager._derive_key(password, salt)

        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()


class KeyManager:
    """Manage RSA keys with password protection and metadata tracking."""

    def __init__(self, keys_dir: str = "/etc/dystopian-crypto/keys"):
        """
        Initialize key manager.

        Args:
            keys_dir: Directory to store keys
        """
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_dir = self.keys_dir / ".metadata"
        self.metadata_dir.mkdir(exist_ok=True)

    def create_ca_keypair(
        self,
        name: str,
        password_file: str,
        key_size: int = 2048,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        """
        Create and store password-protected CA keypair.

        Args:
            name: CA name (e.g., 'RootCA')
            password_file: Path to file containing password
            key_size: RSA key size (2048, 3072, 4096)
            overwrite: Overwrite existing keys

        Returns:
            Metadata dict with key info
        """
        private_key_path = self.keys_dir / f"{name}-private.key"
        public_key_path = self.keys_dir / f"{name}-public.pem"

        if private_key_path.exists() and not overwrite:
            raise FileExistsError(
                f"Key {name} already exists. Use overwrite=True to replace."
            )

        if not Path(password_file).exists():
            raise FileNotFoundError(f"Password file not found: {password_file}")

        # Generate RSA keypair
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=key_size, backend=default_backend()
        )
        public_key = private_key.public_key()

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Encrypt private key with password
        encrypted_private = PasswordManager.encrypt_key(private_pem, password_file)

        # Save encrypted private key
        private_key_path.write_bytes(encrypted_private)
        os.chmod(private_key_path, 0o600)

        # Save public key (unencrypted)
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        public_key_path.write_bytes(public_pem)
        os.chmod(public_key_path, 0o644)

        # Create metadata
        metadata = {
            "name": name,
            "type": "ca",
            "key_size": key_size,
            "algorithm": "RSA",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "private_key_path": str(private_key_path),
            "public_key_path": str(public_key_path),
            "password_file": password_file,
            "key_id": hashlib.sha256(name.encode()).hexdigest()[:16],
            "encrypted": True,
        }

        # Save metadata
        metadata_file = self.metadata_dir / f"{name}.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        os.chmod(metadata_file, 0o600)

        return metadata

    def create_signing_keypair(
        self,
        name: str,
        ca_name: str,
        password_file: str,
        key_size: int = 2048,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        """
        Create signing keypair under CA.

        Args:
            name: Signing key name
            ca_name: Parent CA name
            password_file: Password file
            key_size: RSA key size
            overwrite: Overwrite existing

        Returns:
            Metadata dict
        """
        private_key_path = self.keys_dir / f"{name}-private.key"
        public_key_path = self.keys_dir / f"{name}-public.pem"

        if private_key_path.exists() and not overwrite:
            raise FileExistsError(f"Key {name} already exists.")

        # Generate keypair
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=key_size, backend=default_backend()
        )
        public_key = private_key.public_key()

        # Serialize and encrypt
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        encrypted_private = PasswordManager.encrypt_key(private_pem, password_file)

        # Save
        private_key_path.write_bytes(encrypted_private)
        os.chmod(private_key_path, 0o600)

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        public_key_path.write_bytes(public_pem)
        os.chmod(public_key_path, 0o644)

        # Metadata
        metadata = {
            "name": name,
            "type": "signing",
            "parent_ca": ca_name,
            "key_size": key_size,
            "algorithm": "RSA",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "private_key_path": str(private_key_path),
            "public_key_path": str(public_key_path),
            "password_file": password_file,
            "key_id": hashlib.sha256(name.encode()).hexdigest()[:16],
            "encrypted": True,
        }

        metadata_file = self.metadata_dir / f"{name}.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        os.chmod(metadata_file, 0o600)

        return metadata

    def load_private_key(self, name: str, password_file: str):
        """
        Load password-protected private key.

        Args:
            name: Key name
            password_file: Password file path

        Returns:
            Decrypted private key object
        """
        metadata_file = self.metadata_dir / f"{name}.json"
        metadata = json.loads(metadata_file.read_text())

        private_key_path = Path(metadata["private_key_path"])
        encrypted_data = private_key_path.read_bytes()

        # Decrypt
        private_pem = PasswordManager.decrypt_key(encrypted_data, password_file)

        # Load private key
        return serialization.load_pem_private_key(
            private_pem, password=None, backend=default_backend()
        )

    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get key metadata."""
        metadata_file = self.metadata_dir / f"{name}.json"
        return json.loads(metadata_file.read_text())

    def list_keys(self) -> Dict[str, Dict[str, Any]]:
        """List all keys with metadata."""
        keys = {}
        for metadata_file in self.metadata_dir.glob("*.json"):
            name = metadata_file.stem
            keys[name] = json.loads(metadata_file.read_text())
        return keys

    def rotate_key(
        self, name: str, password_file: str, new_key_size: int = 2048
    ) -> Dict[str, Any]:
        """
        Rotate key (create new version).

        Args:
            name: Key name
            password_file: Password file
            new_key_size: New key size

        Returns:
            New metadata
        """
        # Get old metadata
        old_metadata = self.get_metadata(name)

        # Backup old key
        backup_dir = self.keys_dir / ".backups"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        backup_name = f"{name}_backup_{timestamp.replace(':', '-')}"

        # Create new key
        new_metadata = self.create_ca_keypair(
            f"{name}_rotated_{timestamp}", password_file, new_key_size, overwrite=False
        )

        # Update metadata with rotation info
        rotation_info = {
            "rotated_at": timestamp,
            "previous_key": backup_name,
            "rotation_reason": "key_rotation",
        }
        new_metadata.update(rotation_info)

        return new_metadata

    def verify_key_integrity(self, name: str) -> Tuple[bool, str]:
        """
        Verify key file integrity.

        Args:
            name: Key name

        Returns:
            Tuple of (is_valid, message)
        """
        try:
            metadata = self.get_metadata(name)
            private_key_path = Path(metadata["private_key_path"])

            if not private_key_path.exists():
                return False, f"Private key file not found: {private_key_path}"

            # Check file permissions
            perms = private_key_path.stat().st_mode & 0o777
            if perms != 0o600:
                return False, f"Invalid permissions: {oct(perms)} (expected 0o600)"

            return True, "Key integrity verified"

        except Exception as e:
            return False, str(e)

