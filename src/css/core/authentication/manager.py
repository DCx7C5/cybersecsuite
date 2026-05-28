"""User authentication — JWT + API key management (Phase 7).

Provides:
- JWT token issuing/validation (HS256 + RS256)
- API key generation/hashing (bcrypt)
- FastAPI Depends() integration for protected endpoints
- Refresh token support
- Logout/revocation
"""

from css.core.logger import getLogger
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from css.core.base.endpoint import BaseEndpoint

log = getLogger(__name__)

# JWT algorithms supported
ALGORITHM_HS256 = "HS256"
ALGORITHM_RS256 = "RS256"

_ph = PasswordHasher()


# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────

class TokenPayload(BaseEndpoint, kw_only=True):
    """JWT token payload."""
    sub: str
    exp: float
    iat: float
    type: str = "access"
    scopes: list[str] = []


class AccessTokenResponse(BaseEndpoint, kw_only=True):
    """Response after token issuance."""
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class APIKeyResponse(BaseEndpoint, kw_only=True):
    """Response after API key generation."""
    key_id: str
    secret: str
    created_at: str
    note: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# JWT Manager
# ─────────────────────────────────────────────────────────────────────────────

class JWTManager:
    """JWT token issuing and validation."""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = ALGORITHM_HS256,
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        """Initialize JWT manager.
        
        Args:
            secret_key: Secret key for HS256 or path to private key for RS256
            algorithm: JWT algorithm (HS256 or RS256)
            access_token_expire_minutes: Access token TTL
            refresh_token_expire_days: Refresh token TTL
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=refresh_token_expire_days)
    
    def issue_tokens(
        self,
        subject: str,
        scopes: Optional[list[str]] = None,
    ) -> tuple[str, Optional[str]]:
        """Issue access and refresh tokens.
        
        Args:
            subject: User ID or principal identifier
            scopes: Authorization scopes for token
            
        Returns:
            Tuple of (access_token, refresh_token)
        """
        now = datetime.now(timezone.utc)
        
        # Access token
        access_payload = {
            "sub": subject,
            "iat": now,
            "exp": now + self.access_token_expire,
            "type": "access",
            "scopes": scopes or [],
        }
        access_token = jwt.encode(
            access_payload,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        # Refresh token
        refresh_payload = {
            "sub": subject,
            "iat": now,
            "exp": now + self.refresh_token_expire,
            "type": "refresh",
        }
        refresh_token = jwt.encode(
            refresh_payload,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        log.debug(f"Issued tokens for {subject}")
        return access_token, refresh_token
    
    def validate_token(self, token: str, expected_type: str = "access") -> Optional[TokenPayload]:
        """Validate JWT token.
        
        Args:
            token: JWT token string
            expected_type: Expected token type (access/refresh)
            
        Returns:
            TokenPayload if valid, None if invalid/expired
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            if payload.get("type") != expected_type:
                log.warning(f"Token type mismatch: expected {expected_type}, got {payload.get('type')}")
                return None
            
            return TokenPayload(**payload)
        
        except jwt.ExpiredSignatureError:
            log.debug("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            log.debug(f"Invalid token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str, scopes: Optional[list[str]] = None) -> Optional[str]:
        """Issue new access token from refresh token.
        
        Args:
            refresh_token: Refresh token string
            scopes: New scopes for access token (default: keep from refresh)
            
        Returns:
            New access token if refresh valid, None otherwise
        """
        payload = self.validate_token(refresh_token, expected_type="refresh")
        if not payload:
            return None
        
        subject = payload.sub
        token, _ = self.issue_tokens(subject, scopes or payload.scopes)
        log.debug(f"Refreshed access token for {subject}")
        return token


# ─────────────────────────────────────────────────────────────────────────────
# API Key Manager
# ─────────────────────────────────────────────────────────────────────────────

class APIKeyManager:
    """API key generation and validation."""
    
    @staticmethod
    def generate_key_pair(key_id: str, note: Optional[str] = None) -> tuple[str, str]:
        """Generate API key pair (ID + secret).
        
        Args:
            key_id: Key identifier (e.g., "sk_prod_xyz")
            note: Optional description
            
        Returns:
            Tuple of (key_id, hashed_secret)
        """
        # Generate 32-byte secret
        secret = secrets.token_urlsafe(32)
        
        # Hash for storage
        hashed = _ph.hash(secret)
        
        log.debug(f"Generated API key {key_id}")
        return secret, hashed
    
    @staticmethod
    def verify_key(secret: str, hashed: str) -> bool:
        """Verify API key secret against stored hash.
        
        Args:
            secret: Plain secret from client
            hashed: Hashed secret from storage
            
        Returns:
            True if valid, False otherwise
        """
        try:
            return _ph.verify(hashed, secret)
        except (VerifyMismatchError, VerificationError) as e:
            log.debug(f"Key verification error: {e}")
            return False
    
    @staticmethod
    def hash_key(secret: str) -> str:
        """Hash API key for storage."""
        return _ph.hash(secret)


# ─────────────────────────────────────────────────────────────────────────────
# Password Manager
# ─────────────────────────────────────────────────────────────────────────────

class PasswordManager:
    """Password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using argon2.
        
        Args:
            password: Plain password
            
        Returns:
            Hashed password
        """
        return _ph.hash(password)
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash.
        
        Args:
            password: Plain password from user
            hashed: Hashed password from storage
            
        Returns:
            True if valid, False otherwise
        """
        try:
            return _ph.verify(hashed, password)
        except (VerifyMismatchError, VerificationError) as e:
            log.debug(f"Password verification error: {e}")
            return False


# ─────────────────────────────────────────────────────────────────────────────
# Revocation/Token Blacklist
# ─────────────────────────────────────────────────────────────────────────────

class TokenRevocationStore:
    """In-memory token revocation store (in-memory for now, Redis in production)."""
    
    def __init__(self):
        """Initialize revocation store."""
        self._revoked_tokens: set[str] = set()
        self._revoked_keys: set[str] = set()  # API key IDs
    
    def revoke_token(self, token_id: str) -> None:
        """Revoke a token.
        
        Args:
            token_id: Token identifier to revoke
        """
        self._revoked_tokens.add(token_id)
        log.debug(f"Revoked token {token_id}")
    
    def is_token_revoked(self, token_id: str) -> bool:
        """Check if token is revoked.
        
        Args:
            token_id: Token identifier to check
            
        Returns:
            True if revoked, False otherwise
        """
        return token_id in self._revoked_tokens
    
    def revoke_api_key(self, key_id: str) -> None:
        """Revoke an API key.
        
        Args:
            key_id: API key ID to revoke
        """
        self._revoked_keys.add(key_id)
        log.debug(f"Revoked API key {key_id}")
    
    def is_api_key_revoked(self, key_id: str) -> bool:
        """Check if API key is revoked.
        
        Args:
            key_id: API key ID to check
            
        Returns:
            True if revoked, False otherwise
        """
        return key_id in self._revoked_keys

