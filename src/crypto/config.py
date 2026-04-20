"""
Configuration loader for the cybersec standalone app.
Loads settings from settings.json and provides typed access.
"""
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class KeyDerivationConfig:
    """Argon2id key derivation settings."""
    algorithm: str = "Argon2id"
    memory_cost: int = 262144  # 256 MB
    iterations: int = 4
    lanes: int = 4
    salt_length: int = 32


@dataclass
class EncryptionConfig:
    """AES-256-GCM encryption settings."""
    algorithm: str = "AES-256-GCM"
    nonce_length: int = 12
    tag_length: int = 16


@dataclass
class CryptoConfig:
    """Cryptographic algorithm settings."""
    algorithm: str = "Ed25519"
    hash: str = "blake2b"
    hash_digest_size: int = 32
    key_derivation: KeyDerivationConfig = field(default_factory=KeyDerivationConfig)
    encryption: EncryptionConfig = field(default_factory=EncryptionConfig)


@dataclass
class SigningConfig:
    """Ed25519 signing settings."""
    algorithm: str = "Ed25519"
    token_format: str = "frontmatter.payload"
    default_expiry_hours: int = 8760  # 1 year
    key_id: str = "default"


@dataclass
class ArtifactsConfig:
    """Artifact management settings."""
    checksum_algorithm: str = "blake2b"
    checksum_key: str = "artifact_integrity"
    signature_log_enabled: bool = True
    version_history_limit: int = 50


@dataclass
class KeyPermissions:
    """File permission settings for keys."""
    private_key: str = "0600"
    public_key: str = "0644"
    metadata: str = "0600"


@dataclass
class KeysConfig:
    """Key storage settings."""
    directory: str = "/etc/dystopian/crypto/cert/private"
    metadata_subdir: str = ".metadata"
    backup_subdir: str = ".backups"
    permissions: KeyPermissions = field(default_factory=KeyPermissions)


@dataclass
class CacheConfig:
    """Cache integrity settings."""
    integrity_key: str = "cache_integrity"
    default_ttl_hours: int = 24


@dataclass
class SecurityConfig:
    """Security enforcement settings."""
    min_password_length: int = 16
    require_password_file: bool = True
    audit_logging: bool = True


@dataclass
class AppSettings:
    """Main application settings container."""
    agent: str = "cybersec-agent"
    version: str = "1.0.0"
    crypto: CryptoConfig = field(default_factory=CryptoConfig)
    signing: SigningConfig = field(default_factory=SigningConfig)
    artifacts: ArtifactsConfig = field(default_factory=ArtifactsConfig)
    keys: KeysConfig = field(default_factory=KeysConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppSettings":
        """Create settings from dictionary."""
        crypto_data = data.get("crypto", {})
        crypto = CryptoConfig(
            algorithm=crypto_data.get("algorithm", "Ed25519"),
            hash=crypto_data.get("hash", "blake2b"),
            hash_digest_size=crypto_data.get("hash_digest_size", 32),
            key_derivation=KeyDerivationConfig(**crypto_data.get("key_derivation", {})),
            encryption=EncryptionConfig(**crypto_data.get("encryption", {})),
        )

        signing_data = data.get("signing", {})
        signing = SigningConfig(**signing_data) if signing_data else SigningConfig()

        artifacts_data = data.get("artifacts", {})
        artifacts = ArtifactsConfig(**artifacts_data) if artifacts_data else ArtifactsConfig()

        keys_data = data.get("keys", {})
        keys = KeysConfig(
            directory=keys_data.get("directory", "/etc/dystopian/crypto/cert/private"),
            metadata_subdir=keys_data.get("metadata_subdir", ".metadata"),
            backup_subdir=keys_data.get("backup_subdir", ".backups"),
            permissions=KeyPermissions(**keys_data.get("permissions", {})),
        )

        cache_data = data.get("cache", {})
        cache = CacheConfig(**cache_data) if cache_data else CacheConfig()

        security_data = data.get("security", {})
        security = SecurityConfig(**security_data) if security_data else SecurityConfig()

        return cls(
            agent=data.get("agent", "cybersec-agent"),
            version=data.get("version", "1.0.0"),
            crypto=crypto,
            signing=signing,
            artifacts=artifacts,
            keys=keys,
            cache=cache,
            security=security,
        )

    @classmethod
    def load(cls, path: Optional[str] = None) -> "AppSettings":
        """
        Load settings from JSON file.

        Args:
            path: Path to settings.json (default: project root)

        Returns:
            Loaded AppSettings instance
        """
        if path is None:
            # Default to project root settings.json
            path = Path(__file__).parent.parent.parent / "settings.json"
        else:
            path = Path(path)

        if not path.exists():
            # Return defaults if no config file
            return cls()

        with open(path) as f:
            data = json.load(f)

        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "agent": self.agent,
            "version": self.version,
            "crypto": {
                "algorithm": self.crypto.algorithm,
                "hash": self.crypto.hash,
                "hash_digest_size": self.crypto.hash_digest_size,
                "key_derivation": {
                    "algorithm": self.crypto.key_derivation.algorithm,
                    "memory_cost": self.crypto.key_derivation.memory_cost,
                    "iterations": self.crypto.key_derivation.iterations,
                    "lanes": self.crypto.key_derivation.lanes,
                    "salt_length": self.crypto.key_derivation.salt_length,
                },
                "encryption": {
                    "algorithm": self.crypto.encryption.algorithm,
                    "nonce_length": self.crypto.encryption.nonce_length,
                    "tag_length": self.crypto.encryption.tag_length,
                },
            },
            "signing": {
                "algorithm": self.signing.algorithm,
                "token_format": self.signing.token_format,
                "default_expiry_hours": self.signing.default_expiry_hours,
                "key_id": self.signing.key_id,
            },
            "artifacts": {
                "checksum_algorithm": self.artifacts.checksum_algorithm,
                "checksum_key": self.artifacts.checksum_key,
                "signature_log_enabled": self.artifacts.signature_log_enabled,
                "version_history_limit": self.artifacts.version_history_limit,
            },
            "keys": {
                "directory": self.keys.directory,
                "metadata_subdir": self.keys.metadata_subdir,
                "backup_subdir": self.keys.backup_subdir,
                "permissions": {
                    "private_key": self.keys.permissions.private_key,
                    "public_key": self.keys.permissions.public_key,
                    "metadata": self.keys.permissions.metadata,
                },
            },
            "cache": {
                "integrity_key": self.cache.integrity_key,
                "default_ttl_hours": self.cache.default_ttl_hours,
            },
            "security": {
                "min_password_length": self.security.min_password_length,
                "require_password_file": self.security.require_password_file,
                "audit_logging": self.security.audit_logging,
            },
        }

    def save(self, path: Optional[str] = None) -> None:
        """Save settings to JSON file."""
        if path is None:
            path = Path(__file__).parent.parent.parent / "settings.json"
        else:
            path = Path(path)

        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


# Global settings instance (lazy loaded)
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get or load global settings instance."""
    global _settings
    if _settings is None:
        _settings = AppSettings.load()
    return _settings


def reload_settings(path: Optional[str] = None) -> AppSettings:
    """Reload settings from file."""
    global _settings
    _settings = AppSettings.load(path)
    return _settings

