import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
USE_REDIS = os.getenv("USE_REDIS", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 86400))
MCP_API_KEY = os.getenv("MCP_API_KEY")  # required for auth
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", 60))
AUDIT_LOG_ENABLED = os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"
