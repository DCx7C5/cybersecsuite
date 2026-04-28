"""
SSL-encrypted cryptographic signing for artifacts using Ed25519.
Provides JWT-like token generation with embedded signatures in frontmatter.
"""
import base64
import json
import hashlib
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend

if TYPE_CHECKING:
    from crypto.key_manager import KeyManager

# Runtime import for key manager
try:
    from crypto.key_manager import KeyManager as _KeyManager, PasswordManager as _PasswordManager
except ImportError:
    _KeyManager = None  # type: ignore[misc, assignment]
    _PasswordManager = None  # type: ignore[misc, assignment]


class SSLArtifactSigner:
    """
    SSL-based artifact signer using Ed25519.

    Generates tokens with signature embedded in frontmatter:
    - Header/Frontmatter: algorithm, key_id, created_at, signature
    - Payload: artifact data, checksums, metadata
    """

    def __init__(
        self,
        private_key_path: Optional[str] = None,
        public_key_path: Optional[str] = None,
        key_id: str = "default",
        key_manager: Optional["KeyManager"] = None,
        password_file: Optional[str] = None,
    ):
        """
        Initialize signer with Ed25519 key pair.

        Args:
            private_key_path: Path to PEM-encoded private key
            public_key_path: Path to PEM-encoded public key
            key_id: Key identifier for token headers
            key_manager: Optional KeyManager for password-protected keys
            password_file: Path to password file for encrypted keys
        """
        self.key_id = key_id
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
        self.key_manager = key_manager
        self.password_file = password_file
        self._private_key = None
        self._public_key = None

        if private_key_path and password_file and key_manager is not None:
            # Load encrypted key via KeyManager
            try:
                self._private_key = key_manager.load_private_key(
                    key_id, password_file
                )
            except Exception:
                self._load_private_key()
        elif private_key_path:
            self._load_private_key()

        if public_key_path:
            self._load_public_key()

    def generate_key_pair(
        self, private_key_path: str, public_key_path: str, overwrite: bool = False
    ) -> None:
        """
        Generate Ed25519 key pair and save to PEM files.

        Args:
            private_key_path: Where to save private key
            public_key_path: Where to save public key
            overwrite: If False, skip if keys exist

        Raises:
            FileExistsError: If keys exist and overwrite=False
        """
        if not overwrite and Path(private_key_path).exists():
            raise FileExistsError(f"Private key already exists: {private_key_path}")

        # Generate Ed25519 key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Save private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        Path(private_key_path).write_bytes(private_pem)
        os.chmod(private_key_path, 0o600)  # Secure permissions

        # Save public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        Path(public_key_path).write_bytes(public_pem)

        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
        self._private_key = private_key
        self._public_key = public_key

    def _load_private_key(self) -> None:
        """Load private key from PEM file."""
        if self.private_key_path:
            pem_data = Path(self.private_key_path).read_bytes()
            self._private_key = serialization.load_pem_private_key(
                pem_data, password=None, backend=default_backend()
            )

    def _load_public_key(self) -> None:
        """Load public key from PEM file."""
        if self.public_key_path:
            pem_data = Path(self.public_key_path).read_bytes()
            self._public_key = serialization.load_pem_public_key(
                pem_data, backend=default_backend()
            )

    @staticmethod
    def _base64_encode(data: bytes) -> str:
        """URL-safe base64 encoding."""
        return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

    @staticmethod
    def _base64_decode(data: str) -> bytes:
        """URL-safe base64 decoding."""
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    def sign_artifact(
        self,
        artifact_data: Dict[str, Any],
        expires_in_hours: int = 24,
        custom_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Sign artifact and return token with signature in frontmatter.

        Args:
            artifact_data: Artifact content to sign
            expires_in_hours: Token expiration time
            custom_claims: Additional claims to include

        Returns:
            Signed token: {frontmatter_with_signature}.{payload}
        """
        if not self._private_key:
            raise ValueError("Private key not loaded. Call generate_key_pair() or init with private_key_path.")

        now = datetime.now(timezone.utc)
        exp = now + timedelta(hours=expires_in_hours)

        # Create payload with checksums
        body_hash = hashlib.sha256(
            json.dumps(artifact_data, sort_keys=True).encode()
        ).hexdigest()

        payload = {
            "data": artifact_data,
            "body_hash": body_hash,
            "exp": exp.isoformat(),
            "iat": now.isoformat(),
            **{**(custom_claims or {})},
        }

        # Encode payload first (this is what we sign)
        payload_encoded = self._base64_encode(
            json.dumps(payload, separators=(",", ":")).encode()
        )

        # Sign the payload with Ed25519
        signature = self._private_key.sign(payload_encoded.encode())
        signature_encoded = self._base64_encode(signature)

        # Create frontmatter/headers with signature included
        frontmatter = {
            "alg": "Ed25519",
            "typ": "ARTIFACT",
            "kid": self.key_id,
            "created_at": now.isoformat(),
            "sig": signature_encoded,  # Signature embedded in frontmatter
        }

        frontmatter_encoded = self._base64_encode(
            json.dumps(frontmatter, separators=(",", ":")).encode()
        )

        return f"{frontmatter_encoded}.{payload_encoded}"

    def verify_artifact(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify artifact signature from frontmatter and return payload if valid.

        Args:
            token: Signed token to verify

        Returns:
            Tuple of (is_valid, payload_dict or None)
        """
        if not self._public_key:
            raise ValueError("Public key not loaded. Init with public_key_path.")

        try:
            parts = token.split(".")
            if len(parts) != 2:
                return False, None

            frontmatter_encoded, payload_encoded = parts

            # Decode frontmatter to get signature
            frontmatter_json = self._base64_decode(frontmatter_encoded).decode()
            frontmatter = json.loads(frontmatter_json)

            # Extract signature from frontmatter
            signature_encoded = frontmatter.get("sig")
            if not signature_encoded:
                return False, None

            signature = self._base64_decode(signature_encoded)

            # Verify Ed25519 signature against payload
            try:
                self._public_key.verify(signature, payload_encoded.encode())
            except Exception:
                return False, None

            # Decode and parse payload
            payload_json = self._base64_decode(payload_encoded).decode()
            payload = json.loads(payload_json)

            # Check expiration
            exp_time = datetime.fromisoformat(payload["exp"])
            if datetime.now(timezone.utc) > exp_time:
                return False, None

            # Verify body hash
            original_data = payload["data"]
            body_hash = hashlib.sha256(
                json.dumps(original_data, sort_keys=True).encode()
            ).hexdigest()
            if body_hash != payload["body_hash"]:
                return False, None

            return True, payload

        except Exception:
            return False, None

    def get_signature_metadata(self, token: str) -> Optional[Dict[str, Any]]:
        """Extract frontmatter metadata including signature."""
        try:
            parts = token.split(".")
            if len(parts) != 2:
                return None
            frontmatter_json = self._base64_decode(parts[0]).decode()
            return json.loads(frontmatter_json)
        except BaseException(Exception):
            return None

