from os import getenv
from pathlib import Path


# ── General Settings ──────────────────────────────────────────────────────────

DEBUG = False
PROJECT_DIR = Path(__file__).resolve().parent

AUTO_CREATE_POSTGRES_DB = f"{getenv('AUTO_CREATE_DATABASE', 'true')}"
LOG_LEVEL = f"{getenv('LOG_LEVEL', 'info')}"


# ── Redis Database ──────────────────────────────────────────────────────────

REDIS_DATABASE = {
    "host": f"{getenv('REDIS_HOST', 'localhost')}",
    "port": f"{getenv('REDIS_PORT', '6379')}",
    "db": 0,
}


# ── Postgres Database ──────────────────────────────────────────────────────────

POSTGRES_DATABASE = {
    "host": f"{getenv('CYBERSEC_DB_HOST', None)}",  # None to use unix socket
    "port": f"{getenv('CYBERSEC_DB_PORT', None)}",  # None to use unix socket
    "user": f"{getenv('CYBERSEC_DB_USER', 'cybersec')}",
    "password": f"{getenv('CYBERSEC_DB_PASSWORD', 'change_me')}",
    "database": f"{getenv('CYBERSEC_DB_NAME', 'cybersec_forensics')}",
}


# ── OpenTelemetry / OpenObserve (LLM layer) ───────────────────────────────────

OPEN_OBSERVE = {
    "email": f"{getenv('OPENOBSERVE_EMAIL', 'admin@cybersec.local')}",
    "password": f"{getenv('OPENOBSERVE_PASSWORD', 'cYb3rS3c!')}",
    "endpoint": f"{getenv('OPENOBSERVE_OTLP_ENDPOINT', 'http://127.0.0.1:5080/api/default')}",
    "service_name": f"{getenv('OTEL_SERVICE_NAME', 'css-llm')}",
}


# ── A2A server ────────────────────────────────────────────────────────────────

A2A_SERVER = {
    "host": f"{getenv('A2A_HOST', '127.0.0.1')}",
    "port": f"{getenv('A2A_PORT', '8000')}",
    "base_url": f"{getenv('A2A_BASE_URL', 'http_')}",
}

# ── Chat Settings ────────────────────────────────────────────────────────────────

QOL_MAX_TOKENS = f"{getenv('QOL_MAX_TOKENS', '100')}"


