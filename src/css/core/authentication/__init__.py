"""User authentication — JWT + API key management.

Located in core (not modules) because this is user-level auth (not provider auth).
Provider auth (LLM credentials) lives in api_services module.
"""

from .manager import (
    JWTManager,
    APIKeyManager,
    PasswordManager,
    TokenRevocationStore,
    TokenPayload,
    AccessTokenResponse,
    APIKeyResponse,
    ALGORITHM_HS256,
    ALGORITHM_RS256,
)
from .endpoints import router

__all__ = [
    "JWTManager",
    "APIKeyManager",
    "PasswordManager",
    "TokenRevocationStore",
    "TokenPayload",
    "AccessTokenResponse",
    "APIKeyResponse",
    "ALGORITHM_HS256",
    "ALGORITHM_RS256",
    "router",
]
