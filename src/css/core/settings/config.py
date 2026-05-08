from os import getenv
from pathlib import Path


# ── General Settings ──────────────────────────────────────────────────────────

DEBUG = bool(getenv('DEBUG', 'false'))
ENVIRONMENT = getenv('ENVIRONMENT', 'development')
PROJECT_DIR = Path(__file__).resolve().parent
PYTHONUNBUFFERED = True

AUTO_CREATE_POSTGRES_DB = bool(getenv('AUTO_CREATE_DATABASE', 'true'))
LOG_LEVEL = 'DEBUG' if DEBUG else getenv('LOG_LEVEL', 'INFO').upper()

# ── Module Import Order ──────────────────────────────────────────────────────────

MODULES = [
    # Foundation / orchestration dependencies
    "css.modules.css_a2a",
    "css.modules.tools",
    "css.modules.skills",
    "css.modules.tasks",
    "css.modules.teams",
    "css.modules.agents",
    "css.modules.tags",
    # Routing/classification chain (triage -> strategies -> chat)
    "css.modules.triage",
    "css.modules.strategies",
    "css.modules.chat",
    # Planning and external A2A
    "css.modules.planer",
    "css.modules.google_a2a",
    # Domain modules (mostly independent)
    "css.modules.alerts",
    "css.modules.compliance",
    "css.modules.evidence",
    "css.modules.incidents",
    "css.modules.knowledge",
    "css.modules.local_assist",
    "css.modules.mcps",
    "css.modules.mitre",
    "css.modules.obsidian_memory",
    "css.modules.projects",
    "css.modules.prompts",
    "css.modules.reports",
    "css.modules.scans",
    "css.modules.scheduler",
    "css.modules.threat_intel",
    "css.modules.webhooks",
    "css.modules.workflows",
]


# ── Cache Configuration (Unified @cache Module) ────────────────────────────────

CACHE_ENABLED = bool(getenv('CACHE_ENABLED', 'true'))
CACHE_BACKENDS = getenv('CACHE_BACKENDS', 'redis,postgres,disk').split(',')  # Fallback order
CACHE_DEFAULT_TTL = int(getenv('CACHE_DEFAULT_TTL', '86400'))  # 1 day in seconds

# Cache-specific TTLs
CACHE_LLM_TTL = int(getenv('CACHE_LLM_TTL', '2592000'))  # 30 days
CACHE_KB_TTL = int(getenv('CACHE_KB_TTL', str(CACHE_DEFAULT_TTL)))  # Session lifetime
CACHE_TASK_RESULT_TTL = int(getenv('CACHE_TASK_RESULT_TTL', str(CACHE_DEFAULT_TTL * 10)))  # Phase + 7 days
CACHE_A2A_TTL = int(getenv('CACHE_A2A_TTL', '604800'))  # 7 days (team lifetime)
CACHE_HEARTBEAT_TTL = int(getenv('CACHE_HEARTBEAT_TTL', '30'))  # 30 seconds
CACHE_CONFIG_TTL = int(getenv('CACHE_CONFIG_TTL', '3600'))  # 1 hour

# Cache compression & encryption
CACHE_COMPRESSION = getenv('CACHE_COMPRESSION', 'gzip')  # 'gzip' or 'none'
CACHE_ENCRYPTION = bool(getenv('CACHE_ENCRYPTION', 'true'))
CACHE_METRICS = bool(getenv('CACHE_METRICS', 'true'))

# Disk cache (L4 fallback)
CACHE_DISK_PATH = getenv('CACHE_DISK_PATH', '/var/cache/css/')
CACHE_DISK_SIZE_MB = int(getenv('CACHE_DISK_SIZE_MB', '1000'))


# ── Redis Database (L2 Cache) ──────────────────────────────────────────────────
DATABASES = {
    "POSTGRES": {
        "url": getenv('DATABASE_URL', None),
    },
    "REDIS": {

    },
    "OPENOBSERVE": {

    }
}
REDIS_URL = getenv('REDIS_URL', 'redis://localhost:6379')
REDIS_HOST = getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(getenv('REDIS_PORT', '6379'))
REDIS_DB = int(getenv('REDIS_DB', '1'))
REDIS_PASSWORD = getenv('REDIS_PASSWORD', None)

REDIS_DATABASE = {
    'url': REDIS_URL,
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_DB,
    'password': REDIS_PASSWORD,
    'decode_responses': True,
    'socket_keepalive': True,
    'health_check_interval': 30,
}

# Redis configuration for multi-orchestrator shared cache
REDIS_CONFIG = {
    'maxmemory': '1024mb',
    'maxmemory_policy': 'allkeys-lru',
    'appendonly': 'yes',
    'appendfsync': 'everysec',
}


# ── Postgres Database (L3 Persistence) ──────────────────────────────────────────

DATABASE_URL = getenv('DATABASE_URL', None)  # Full URL if provided


POSTGRES_DATABASE = {
    'url': getenv('DATABASE_URL', None),
    'host': getenv('CYBERSEC_DB_HOST', getenv('POSTGRES_HOST', None)),  # None for Unix socket,
    'port': getenv('CYBERSEC_DB_PORT', getenv('POSTGRES_PORT', '5432')),
    'user': getenv('CYBERSEC_DB_USER', getenv('POSTGRES_USER', 'cybersec')),
    'password': getenv('CYBERSEC_DB_PASSWORD', getenv('POSTGRES_PASSWORD', 'change_me')),
    'database': getenv('CYBERSEC_DB_NAME', getenv('POSTGRES_DB', 'cybersec')),
    'driver': 'asyncpg',
    'min_size': 5,
    'max_size': 20,
    'max_cached_statement_lifetime': 300,
    'max_cacheable_statement_size': 15000,
}

# PostgreSQL cache storage
CACHE_POSTGRES_TABLE = getenv('CACHE_POSTGRES_TABLE', 'cache_entries')
CACHE_POSTGRES_ARCHIVE = bool(getenv('CACHE_POSTGRES_ARCHIVE', 'true'))


# ── OpenTelemetry / OpenObserve (Observability) ───────────────────────────────

OPENOBSERVE_HOST = getenv('OPENOBSERVE_HOST', 'localhost')
OPENOBSERVE_PORT = int(getenv('OPENOBSERVE_PORT', '5080'))


OPEN_OBSERVE = {
    'email': getenv('ZO_ROOT_USER_EMAIL', 'admin@css.local'),
    'password': getenv('ZO_ROOT_USER_PASSWORD', 'change_me'),
    'host': OPENOBSERVE_HOST,
    'port': OPENOBSERVE_PORT,
    'endpoint': getenv('OPENOBSERVE_OTLP_ENDPOINT', f'http://{OPENOBSERVE_HOST}:{OPENOBSERVE_PORT}/api/default'),
    'service_name': getenv('OTEL_SERVICE_NAME', 'css-backend'),
}

# Telemetry indices
TELEMETRY_ENABLED = bool(getenv('TELEMETRY_ENABLED', 'true'))
AUDIT_LOG_ENABLED = bool(getenv('AUDIT_LOG_ENABLED', 'true'))


# ── LLM API Services Configuration ──────────────────────────────────────────────


# Local LLM (Ollama)
OLLAMA_API_URL = getenv('OLLAMA_API_URL', 'http://localhost:11434')
OLLAMA_MODEL = getenv('OLLAMA_MODEL', 'qwen3:0.6b')  # For Triage role
OLLAMA_TIMEOUT = int(getenv('OLLAMA_TIMEOUT', '120'))

# LLM API caching (reduces costs)
LLM_CACHE_ENABLED = bool(getenv('LLM_CACHE_ENABLED', 'true'))
LLM_CACHE_TTL = CACHE_LLM_TTL  # 30 days


# ── A2A Communication (Agent-to-Agent) ──────────────────────────────────────────

# Custom A2A (@css_a2a module)
CSS_A2A_ENABLED = bool(getenv('CSS_A2A_ENABLED', 'true'))
CSS_A2A_KB_SIZE_MB = int(getenv('CSS_A2A_KB_SIZE_MB', '100'))
CSS_A2A_MESSAGE_TIMEOUT_SEC = int(getenv('CSS_A2A_MESSAGE_TIMEOUT_SEC', '5'))

# Google A2A (@google_a2a module)
GOOGLE_A2A_ENABLED = bool(getenv('GOOGLE_A2A_ENABLED', 'false'))

A2A_SERVER = {
    'host': getenv('A2A_HOST', '127.0.0.1'),
    'port': int(getenv('A2A_PORT', '8000')),
    'base_url': getenv('A2A_BASE_URL', 'http://localhost:8000'),
}


# ── Orchestrator Configuration ──────────────────────────────────────────────────

ORCHESTRATOR_HEARTBEAT_INTERVAL_SEC = int(getenv('ORCHESTRATOR_HEARTBEAT_INTERVAL_SEC', '30'))
ORCHESTRATOR_CRASH_TIMEOUT_SEC = int(getenv('ORCHESTRATOR_CRASH_TIMEOUT_SEC', '300'))  # 5 min
ORCHESTRATOR_TASK_TIMEOUT_SEC = int(getenv('ORCHESTRATOR_TASK_TIMEOUT_SEC', '3600'))  # 1 hour

# Multi-orchestrator mode
MULTI_ORCHESTRATOR_ENABLED = bool(getenv('MULTI_ORCHESTRATOR_ENABLED', 'true'))
MAX_ORCHESTRATORS_DEV = int(getenv('MAX_ORCHESTRATORS_DEV', '3'))
MAX_ORCHESTRATORS_OTHER = int(getenv('MAX_ORCHESTRATORS_OTHER', '2'))


# ── Session Modes ──────────────────────────────────────────────────────────────

SESSION_MODE = getenv('SESSION_MODE', 'development')  # development, red_team, blue_team, purple_team
ALLOWED_MODES = ['development', 'red_team', 'blue_team', 'purple_team']

# Mode-specific settings
SESSION_TIMEOUT_MINUTES = int(getenv('SESSION_TIMEOUT_MINUTES', '480'))  # 8 hours


# ── Frontend Configuration ──────────────────────────────────────────────────────

FRONTEND_HOST = getenv('FRONTEND_HOST', 'localhost')
FRONTEND_PORT = int(getenv('FRONTEND_PORT', '8000'))
FRONTEND_HTTPS_PORT = int(getenv('FRONTEND_HTTPS_PORT', '8443'))

REACT_APP_API_URL = getenv('REACT_APP_API_URL', 'http://localhost:3000')
REACT_APP_WS_URL = getenv('REACT_APP_WS_URL', 'ws://localhost:3000/ws')


# ── Backend (ASGI) Configuration ───────────────────────────────────────────────

BACKEND_HOST = getenv('BACKEND_HOST', '127.0.0.1')
BACKEND_PORT = int(getenv('BACKEND_PORT', '8000'))

# ASGI server
ASGI_WORKERS = int(getenv('ASGI_WORKERS', '4'))
ASGI_WORKER_CLASS = getenv('ASGI_WORKER_CLASS', 'uvicorn.workers.UvicornWorker')
ASGI_ACCESS_LOG = bool(getenv('ASGI_ACCESS_LOG', 'true'))


# ── Logging Configuration ──────────────────────────────────────────────────────

LOG_FILE_NAME = getenv('LOG_FILE_NAME', 'asgi.log')
LOG_FORMAT = getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG_DATE_FORMAT = getenv('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
LOG_FILE_MAX_BYTES = int(getenv('LOG_FILE_MAX_BYTES', str(1024 * 1024)))
LOG_FILE_BACKUP_COUNT = int(getenv('LOG_FILE_BACKUP_COUNT', '5'))
LOG_TO_STDOUT = getenv('LOG_TO_STDOUT', 'true').lower() == 'true'
LOG_TO_FILE = getenv('LOG_TO_FILE', 'true').lower() == 'true'

# ── File Paths & Directories ───────────────────────────────────────────────────

BASE_DIR = PROJECT_DIR.parent.parent
CSS_DIR = getenv('CSS_DIR', str(BASE_DIR / 'css'))
CACHE_DIR = getenv('CACHE_DIR', CACHE_DISK_PATH)
LOG_DIR = getenv('LOG_DIR', str(Path.home() / '.css' / 'logs'))
LOG_FILE_PATH = str(Path(LOG_DIR) / LOG_FILE_NAME)

# Ensure directories exist
if not Path(CACHE_DIR).exists():
    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

if not Path(LOG_DIR).exists():
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)


# ── Security & Secrets ─────────────────────────────────────────────────────────

# API Keys (from environment)
SECRET_KEY = getenv('SECRET_KEY', 'change-me-in-production')
JWT_SECRET = getenv('JWT_SECRET', SECRET_KEY)
JWT_ALGORITHM = getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(getenv('JWT_EXPIRATION_HOURS', '24'))

# Encryption
ENCRYPTION_ENABLED = getenv('ENCRYPTION_ENABLED', 'true').lower() == 'true'
ENCRYPTION_KEY = getenv('ENCRYPTION_KEY', '')  # Must be set in production


# ── Performance Tuning ──────────────────────────────────────────────────────────

# Connection pooling
DB_POOL_MIN_SIZE = int(getenv('DB_POOL_MIN_SIZE', '5'))
DB_POOL_MAX_SIZE = int(getenv('DB_POOL_MAX_SIZE', '20'))

# Async concurrency
MAX_CONCURRENT_TASKS = int(getenv('MAX_CONCURRENT_TASKS', '100'))
MAX_CONCURRENT_AGENTS = int(getenv('MAX_CONCURRENT_AGENTS', '50'))


# ── Chat Settings ────────────────────────────────────────────────────────

QOL_MAX_TOKENS = int(getenv('QOL_MAX_TOKENS', '100'))
QOL_TOKEN_COUNTER = bool(getenv('QOL_TOKEN_COUNTER', 'true'))
CHAT_CONTEXT_WINDOW = int(getenv('CHAT_CONTEXT_WINDOW', '4096'))


# ── Api Keys ────────────────────────────────────────────────────────


# ── Marketplace Configuration ───────────────────────────────────────

MARKETPLACE_CONFIG = {
    'index_url': getenv(
        'MARKETPLACE_INDEX_URL',
        'https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json'
    ),
    'index_hash_url': getenv(
        'MARKETPLACE_INDEX_HASH_URL',
        'https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json.sha512'
    ),
    'base_url': getenv(
        'MARKETPLACE_BASE_URL',
        'https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main'
    ),
    'install_root': getenv('MARKETPLACE_INSTALL_ROOT', '~/.css/packages'),
    'update_check_interval': int(getenv('MARKETPLACE_UPDATE_CHECK_INTERVAL', '3600')),  # 1 hour
    'download_timeout': int(getenv('MARKETPLACE_DOWNLOAD_TIMEOUT', '60')),  # seconds
    'max_package_size': int(getenv('MARKETPLACE_MAX_PACKAGE_SIZE', str(100 * 1024 * 1024))),  # 100MB
}

# Marketplace cache configuration
MARKETPLACE_CACHE_TTL_SECONDS = int(getenv('MARKETPLACE_CACHE_TTL', '86400'))  # 1 day
MARKETPLACE_MAX_RESULTS = int(getenv('MARKETPLACE_MAX_RESULTS', '100'))
MARKETPLACE_PAGE_SIZE = int(getenv('MARKETPLACE_PAGE_SIZE', '20'))

# Marketplace HTTP client configuration
MARKETPLACE_SEEDER_HTTP_TIMEOUT = int(getenv('MARKETPLACE_SEEDER_HTTP_TIMEOUT', '30'))  # seconds
