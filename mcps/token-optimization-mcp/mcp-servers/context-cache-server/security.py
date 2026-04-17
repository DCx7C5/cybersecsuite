from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
from collections import defaultdict

security = HTTPBearer()
_rate_limit_store = defaultdict(list)


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or credentials.credentials != MCP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing MCP API key")
    return credentials.credentials


def rate_limit(client_id: str = "default"):
    now = time.time()
    _rate_limit_store[client_id] = [t for t in _rate_limit_store[client_id] if now - t < 60]
    if len(_rate_limit_store[client_id]) >= RATE_LIMIT_PER_MIN:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    _rate_limit_store[client_id].append(now)
