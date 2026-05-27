"""User authentication — JWT + API key management.

Located in core (not modules) because this is user-level authentication (not provider authentication).
Provider authentication (LLM credentials) lives in api_services module.
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
