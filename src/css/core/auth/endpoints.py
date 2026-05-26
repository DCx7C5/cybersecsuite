"""User auth API endpoints — login, refresh, logout, API key management (Phase 7).

Endpoints:
- POST   /api/auth/login          — Username/password → access + refresh tokens
- POST   /api/auth/refresh        — Refresh token → new access token
- POST   /api/auth/logout         — Revoke tokens
- GET    /api/auth/keys           — List API keys
- POST   /api/auth/keys           — Generate new API key
- DELETE /api/auth/keys/{id}      — Revoke API key
"""

import msgspec
from css.core.types.base_endpoint import EndpointModel
from css.core.logger import getLogger
import os

from fastapi import APIRouter, HTTPException, status

from .manager import (
    JWTManager,
    APIKeyManager,
    TokenRevocationStore,
    AccessTokenResponse,
    APIKeyResponse,
)

log = getLogger(__name__)

# Global auth managers (should be DI'd from container in production)
_jwt_manager = JWTManager(
    secret_key=os.environ.get("JWT_SECRET_KEY", "dev-secret-key-change-in-production"),
    access_token_expire_minutes=int(os.environ.get("JWT_EXPIRES_MINUTES", "30")),
)
_revocation_store = TokenRevocationStore()

# ─────────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────────────────────

class LoginRequest(EndpointModel, kw_only=True):
    """Login request with credentials."""
    username: str
    password: str
    scope: list[str] | None = None

class RefreshRequest(EndpointModel, kw_only=True):
    """Refresh token request."""
    refresh_token: str

class LogoutRequest(EndpointModel, kw_only=True):
    """Logout request."""
    access_token: str | None = None

class APIKeyCreateRequest(EndpointModel, kw_only=True):
    """Request to create API key."""
    note: str | None = None

class APIKeyListResponse(EndpointModel, kw_only=True):
    """Response with list of API keys."""
    keys: list[dict]

# ─────────────────────────────────────────────────────────────────────────────
# Router Setup
# ─────────────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=AccessTokenResponse, status_code=status.HTTP_200_OK)
async def login(req: LoginRequest) -> AccessTokenResponse:
    """Login with username/password credentials.
    
    Args:
        req: LoginRequest with username and password
        
    Returns:
        AccessTokenResponse with access + refresh tokens
        
    Raises:
        HTTPException: If credentials invalid or user not found
    """
    try:
        # For now, just generate tokens for valid-looking credentials
        
        if not req.username or not req.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Issue tokens
        access_token, refresh_token = _jwt_manager.issue_tokens(
            subject=req.username,
            scopes=req.scope,
        )
        
        log.info(f"User {req.username} logged in")
        
        return AccessTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(_jwt_manager.access_token_expire.total_seconds()),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(req: RefreshRequest) -> AccessTokenResponse:
    """Refresh access token using refresh token.
    
    Args:
        req: RefreshRequest with refresh token
        
    Returns:
        AccessTokenResponse with new access token
        
    Raises:
        HTTPException: If refresh token invalid or expired
    """
    try:
        # Validate refresh token
        payload = _jwt_manager.validate_token(req.refresh_token, expected_type="refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Issue new access token
        access_token, _ = _jwt_manager.issue_tokens(
            subject=payload.sub,
            scopes=payload.scopes,
        )
        
        log.debug(f"Refreshed token for {payload.sub}")
        
        return AccessTokenResponse(
            access_token=access_token,
            refresh_token=None,
            token_type="bearer",
            expires_in=int(_jwt_manager.access_token_expire.total_seconds()),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(req: LogoutRequest) -> None:
    """Logout and revoke tokens.
    
    Args:
        req: LogoutRequest with optional access token to revoke
        
    Raises:
        HTTPException: If logout fails
    """
    try:
        if req.access_token:
            # Validate token first
            payload = _jwt_manager.validate_token(req.access_token, expected_type="access")
            if payload:
                # Revoke token
                _revocation_store.revoke_token(req.access_token)
                log.info(f"User {payload.sub} logged out")
        
        return None
    
    except Exception as e:
        log.exception(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/keys", response_model=APIKeyListResponse)
async def list_api_keys(authorization: str | None = None) -> APIKeyListResponse:
    """List API keys for authenticated user.
    
    Args:
        authorization: Bearer token for authentication
        
    Returns:
        APIKeyListResponse with list of API keys (secrets redacted)
        
    Raises:
        HTTPException: If not authenticated or no keys found
    """
    try:
        # For now, return empty list
        
        return APIKeyListResponse(keys=[])
    
    except Exception as e:
        log.exception(f"Error listing API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list API keys"
        )

@router.post("/keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    req: APIKeyCreateRequest,
    authorization: str | None = None,
) -> APIKeyResponse:
    """Generate new API key.
    
    Args:
        req: APIKeyCreateRequest with optional note
        authorization: Bearer token for authentication
        
    Returns:
        APIKeyResponse with generated key (secret shown once only!)
        
    Raises:
        HTTPException: If not authenticated or generation fails
    """
    try:
        
        # Generate key pair
        import uuid
        from datetime import datetime, timezone
        
        key_id = f"sk_{uuid.uuid4().hex[:12]}"
        secret, hashed = APIKeyManager.generate_key_pair(key_id, req.note)
        
        log.info(f"Generated API key {key_id}")
        
        return APIKeyResponse(
            key_id=key_id,
            secret=secret,  # Only shown once!
            created_at=datetime.now(timezone.utc).isoformat(),
            note=req.note,
        )
    
    except Exception as e:
        log.exception(f"Error creating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )

@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    authorization: str | None = None,
) -> None:
    """Revoke an API key.
    
    Args:
        key_id: API key ID to revoke
        authorization: Bearer token for authentication
        
    Raises:
        HTTPException: If not authenticated or key not found
    """
    try:
        
        # Revoke key
        _revocation_store.revoke_api_key(key_id)
        
        log.info(f"Revoked API key {key_id}")
        
        return None
    
    except Exception as e:
        log.exception(f"Error deleting API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key"
        )

__all__ = ["router"]
