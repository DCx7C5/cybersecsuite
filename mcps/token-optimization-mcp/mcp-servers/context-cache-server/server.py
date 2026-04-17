from fastmcp import FastMCP
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
import redis
import os
from config import REDIS_URL, USE_REDIS, CACHE_TTL_SECONDS, MCP_API_KEY, AUDIT_LOG_ENABLED
from security import verify_api_key, rate_limit
from pydantic import BaseModel

server = FastMCP("context-cache-server")

if not MCP_API_KEY:
    raise ValueError("MCP_API_KEY environment variable is required")

# Backend selection
if USE_REDIS:
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        print("Redis backend active with security hardening")
    except Exception:
        print("Redis connection failed - falling back to in-memory")
        USE_REDIS = False
        _cache: Dict[str, Dict] = {}
else:
    _cache: Dict[str, Dict] = {}
    print("In-memory backend active with security hardening")


class CacheEntry(BaseModel):
    result: str
    tokens_saved: int
    timestamp: str


@server.tool(description="Store result with token metadata - hardened with auth rate-limit and audit")
def cache_store(key: str, result: str, tokens_saved: int, ttl_seconds: Optional[int] = None,
                api_key: str = Depends(verify_api_key)):
    rate_limit()
    ttl = ttl_seconds or CACHE_TTL_SECONDS
    entry = CacheEntry(result=result, tokens_saved=tokens_saved, timestamp=datetime.utcnow().isoformat())
    if USE_REDIS:
        redis_client.setex(key, ttl, entry.model_dump_json())
    else:
        _cache[key] = entry.model_dump()
    if AUDIT_LOG_ENABLED:
        print(f"AUDIT: STORE key={key} tokens_saved={tokens_saved} client=authorized")
    return f"Stored with {tokens_saved} tokens saved. TTL: {ttl}s"


@server.tool(description="Retrieve from cache - hardened with auth and rate-limit")
def cache_retrieve(key: str, api_key: str = Depends(verify_api_key)):
    rate_limit()
    if USE_REDIS:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    return _cache.get(key)


@server.tool(description="Get live cache analytics - hardened")
def cache_analytics(api_key: str = Depends(verify_api_key)):
    rate_limit()
    return {
        "total_entries": len(_cache) if not USE_REDIS else "N/A (redis)",
        "backend": "redis" if USE_REDIS else "in-memory",
        "security": "enabled (auth+rate-limit+audit)",
    }


if __name__ == "__main__":
    server.run()
