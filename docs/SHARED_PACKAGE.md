# Shared Utilities Package Specification: `cybersecsuite_mcp_core`

## Purpose & Motivation

### The Problem
12 independent MCPs will implement similar functionality repeatedly:
- **Database patterns:** Async ORM setup, migrations, lifecycle management
- **Caching logic:** TTL-based caching, invalidation strategies
- **Validation:** Pydantic v2 schemas, custom validators, IOC/artifact types
- **Structured logging:** Consistent log formats, context propagation
- **Scope/context:** Investigation scope, user context, request tracing
- **Exception handling:** Domain-specific exceptions, error codes

Without shared utilities, each MCP reimplements these independently, creating:
- ❌ Code duplication (12x)
- ❌ Inconsistent patterns (forensic-mcp does it differently than purple-team-mcp)
- ❌ Maintenance burden (fix bug in 12 places)
- ❌ Testing burden (test each implementation separately)
- ❌ Version drift (caching v0.1.0 in one MCP, v0.1.2 in another)

### The Solution
Single shared package `cybersecsuite_mcp_core` (published on PyPI):
- ✅ Single source of truth
- ✅ Consistent patterns across all MCPs
- ✅ Reduced maintenance (fix once, propagate to all)
- ✅ Unified testing
- ✅ Coordinated versioning (all MCPs pin same version)

---

## Package Structure

```
packages/cybersecsuite_mcp_core/
├── pyproject.toml                 # Project metadata, dependencies, build config
├── README.md                       # Usage guide
├── src/cybersecsuite_mcp_core/
│   ├── __init__.py                # Public API exports
│   ├── db.py                      # Database/ORM patterns (Tortoise)
│   ├── cache.py                   # Caching logic, TTL management
│   ├── validation.py              # Pydantic validators, common schemas
│   ├── logging.py                 # Structured logging setup
│   ├── scope.py                   # Investigation scope, context
│   ├── exceptions.py              # Domain-specific exceptions
│   └── types.py                   # Shared type hints
├── tests/
│   ├── test_db.py
│   ├── test_cache.py
│   ├── test_validation.py
│   ├── test_logging.py
│   ├── test_scope.py
│   └── conftest.py
└── pytest.ini
```

---

## Dependencies & pyproject.toml

### Why These Dependencies?

| Dependency | Version | Reason |
|------------|---------|--------|
| **pydantic** | >=2.0.0 | Field validation, schema generation, JSON serialization |
| **tortoise-orm** | >=0.20.0 | Async ORM for PostgreSQL, shared database patterns |
| **python-json-logger** | >=2.0.4 | Structured JSON logging for centralized log aggregation |
| **redis** | >=5.0.0 | Optional: caching backend (async) |
| **python-dotenv** | >=1.0.0 | Load env-based configuration in shared code |
| **typing-extensions** | >=4.5.0 | Backport newer type hints to Python 3.9+ |

### Example pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "cybersecsuite-mcp-core"
version = "0.1.0"
description = "Shared utilities for CyberSecSuite MCPs"
authors = [
    {name = "CyberSecSuite Team", email = "team@cybersecsuite.dev"}
]
requires-python = ">=3.9"
dependencies = [
    "pydantic>=2.0.0",
    "tortoise-orm>=0.20.0",
    "python-json-logger>=2.0.4",
    "python-dotenv>=1.0.0",
    "typing-extensions>=4.5.0",
]

[project.optional-dependencies]
redis = ["redis[asyncio]>=5.0.0"]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.20.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/cybersecsuite_mcp_core"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## Module Specifications

### `db.py` - Database & ORM Patterns

**Purpose:** Centralized Tortoise ORM setup, migrations, connection pooling.

**Exports:**
```python
from cybersecsuite_mcp_core.db import (
    get_db_connection,
    create_tables,
    BaseModel,
    IntField,
    CharField,
    DatetimeField,
)

# Define models by extending BaseModel
class Artifact(BaseModel):
    id = IntField(pk=True)
    name = CharField(max_length=255)
    path = CharField(max_length=1024)
    created_at = DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "artifacts"
```

**Key Functions:**
```python
async def get_db_connection(
    db_url: str,
    modules: list[str],
    timeout: int = 30,
) -> None:
    """
    Initialize Tortoise ORM connection.
    
    Usage:
        await get_db_connection(
            db_url="postgres://user:pass@localhost/cybersecsuite",
            modules=["forensic_mcp.models", "purple_team_mcp.models"],
        )
    """
    ...

async def create_tables(drop_existing: bool = False) -> None:
    """Create/migrate all registered model tables."""
    ...

async def close_db_connection() -> None:
    """Gracefully close database connections."""
    ...

class BaseModel(TortoiseModel):
    """Base model with common fields and methods."""
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)
    
    class Meta:
        abstract = True
```

---

### `cache.py` - Caching & TTL Management

**Purpose:** Provide async caching with TTL, invalidation, and memory safety.

**Exports:**
```python
from cybersecsuite_mcp_core.cache import (
    Cache,
    RedisCache,
    MemoryCache,
    cached,
    invalidate_pattern,
)

# Simple decorator usage
@cached(ttl=3600)  # Cache for 1 hour
async def expensive_analysis(artifact_path: str) -> dict:
    return await forensic_tool.analyze(artifact_path)

# Result is automatically cached
result1 = await expensive_analysis("/path/to/artifact")
result2 = await expensive_analysis("/path/to/artifact")  # Returns cached
```

**Key Functions:**
```python
class Cache(Protocol):
    """Interface all cache implementations must follow."""
    
    async def get(self, key: str) -> Any | None:
        """Retrieve cached value."""
        ...
    
    async def set(self, key: str, value: Any, ttl: int) -> None:
        """Store value with TTL (seconds)."""
        ...
    
    async def delete(self, key: str) -> None:
        """Remove cached value."""
        ...
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Remove all keys matching pattern (glob). Returns count."""
        ...

class MemoryCache(Cache):
    """In-process LRU cache. Good for development."""
    ...

class RedisCache(Cache):
    """Redis-backed distributed cache. Good for production."""
    
    def __init__(self, redis_url: str = "redis://localhost", max_size: int = 10000):
        ...

def cached(
    ttl: int = 3600,
    cache: Cache | None = None,
    key_prefix: str = "",
) -> Callable:
    """
    Decorator to cache async function results.
    
    Usage:
        @cached(ttl=1800, key_prefix="forensic")
        async def analyze_artifact(path: str) -> dict:
            return await expensive_work(path)
    
    Cache key: {key_prefix}:{function_name}:{args_hash}
    """
    ...

async def invalidate_pattern(pattern: str, cache: Cache | None = None) -> int:
    """Invalidate all cache keys matching pattern."""
    ...
```

---

### `validation.py` - Pydantic Validators & Schemas

**Purpose:** Centralized validation schemas, custom validators, common types.

**Exports:**
```python
from cybersecsuite_mcp_core.validation import (
    IOC,
    Artifact,
    ValidationError,
    validate_sha256,
    validate_domain,
    validate_ip,
    validate_artifact_path,
)

# Use predefined schemas
ioc = IOC(type="sha256", value="abc123...")
artifact = Artifact(path="/evidence/malware.exe", artifact_type="file")
```

**Key Schemas:**
```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class IOC(BaseModel):
    """Indicator of Compromise."""
    type: Literal[
        "sha256", "sha1", "md5",
        "ipv4", "ipv6", "domain",
        "url", "email",
    ]
    value: str
    source: str | None = None
    confidence: Literal["high", "medium", "low"] = "medium"
    
    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str, info):
        """Validate value matches IOC type."""
        ioc_type = info.data.get("type")
        if ioc_type == "sha256":
            if not validate_sha256(v):
                raise ValueError(f"Invalid SHA256: {v}")
        elif ioc_type == "ipv4":
            if not validate_ip(v):
                raise ValueError(f"Invalid IP: {v}")
        # ... more validators
        return v

class Artifact(BaseModel):
    """Forensic artifact."""
    path: str
    artifact_type: Literal[
        "file", "registry", "memory", "event_log", "network",
    ]
    size_bytes: int | None = None
    hash_sha256: str | None = None
    
    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str):
        if not validate_artifact_path(v):
            raise ValueError(f"Invalid artifact path: {v}")
        return v

class AnalysisResult(BaseModel):
    """Standardized analysis output."""
    status: Literal["success", "failure", "partial"]
    iocs: list[IOC] = []
    metadata: dict = {}
    error: str | None = None
    execution_time_ms: float
```

**Custom Validators:**
```python
def validate_sha256(value: str) -> bool:
    """Check if value is valid SHA256 hex string."""
    return bool(re.match(r'^[a-f0-9]{64}$', value.lower()))

def validate_ip(value: str, version: Literal[4, 6] | None = None) -> bool:
    """Validate IPv4 or IPv6 address."""
    try:
        ip = ipaddress.ip_address(value)
        if version and ip.version != version:
            return False
        return True
    except ValueError:
        return False

def validate_domain(value: str) -> bool:
    """Check if value is valid domain."""
    return bool(re.match(
        r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$',
        value.lower()
    ))
```

---

### `logging.py` - Structured Logging

**Purpose:** Consistent JSON logging for ELK/Splunk aggregation.

**Exports:**
```python
from cybersecsuite_mcp_core.logging import (
    setup_logging,
    get_logger,
    log_context,
)

# Set up once at MCP startup
setup_logging(
    level="INFO",
    app_name="forensic-mcp",
    json_format=True,
)

# Get logger in any module
logger = get_logger(__name__)

logger.info("Starting analysis", extra={"artifact": "malware.exe"})

# Context manager for request tracing
with log_context(request_id="req-123", user="analyst"):
    logger.info("Processing request")
```

**Key Functions:**
```python
def setup_logging(
    level: str = "INFO",
    app_name: str = "mcp",
    json_format: bool = True,
    log_file: str | None = None,
) -> None:
    """
    Configure root logger with structured JSON format.
    
    Sets up:
    - JSON formatter (for ELK/Splunk)
    - Console handler
    - File handler (optional)
    - Request context propagation
    """
    ...

def get_logger(name: str) -> logging.Logger:
    """Get logger with propagated request context."""
    logger = logging.getLogger(name)
    return logger

@contextmanager
def log_context(**kwargs) -> Generator:
    """
    Temporarily add fields to all logs in this context.
    
    Usage:
        with log_context(request_id="123", user="analyst"):
            logger.info("message")  # Includes request_id and user
    """
    ...

# Output example:
# {
#   "timestamp": "2024-01-15T10:30:45.123Z",
#   "level": "INFO",
#   "logger": "forensic_mcp.analyzer",
#   "message": "Starting analysis",
#   "app": "forensic-mcp",
#   "artifact": "malware.exe",
#   "request_id": "req-123",
#   "user": "analyst"
# }
```

---

### `scope.py` - Investigation Scope & Context

**Purpose:** Shared patterns for investigation scope, access control, multi-tenancy.

**Exports:**
```python
from cybersecsuite_mcp_core.scope import (
    Scope,
    ScopeContext,
    current_scope,
    set_scope,
)

# Initialize scope for a request
scope = Scope(
    investigation_id="inv-123",
    user_id="analyst-456",
    case_id="case-789",
)

# Use in request handler
async def handle_analysis_request(artifact_path: str):
    async with set_scope(scope):
        # All operations in this block have scope context
        logger.info("Starting analysis")  # Includes scope
        result = await analyze_artifact(artifact_path)
        # Result is tagged with scope
        return result

# Retrieve scope in any function
current = current_scope()
```

**Key Classes:**
```python
class Scope(BaseModel):
    """Investigation scope for multi-tenancy."""
    investigation_id: str
    user_id: str
    case_id: str
    tags: dict[str, str] = {}
    
    def add_tag(self, key: str, value: str) -> None:
        """Add contextual tag."""
        self.tags[key] = value

class ScopeContext:
    """Context manager for scope propagation."""
    
    async def __aenter__(self) -> Scope:
        """Enter scope context."""
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit scope context."""
        ...

def current_scope() -> Scope | None:
    """Get current scope (thread-safe, async-safe)."""
    ...

@contextmanager
def set_scope(scope: Scope) -> Generator:
    """Set scope for synchronous context."""
    ...
```

---

### `exceptions.py` - Domain-Specific Exceptions

**Purpose:** Standardized exception hierarchy for all MCPs.

**Exports:**
```python
from cybersecsuite_mcp_core.exceptions import (
    MCPError,
    ValidationError,
    DatabaseError,
    TimeoutError,
    ToolExecutionError,
)

# Usage in tool
try:
    result = await tool.execute(input)
except MCPError as e:
    logger.error(f"Tool failed: {e.message}", extra={"code": e.code})
    return {"error": e.message, "code": e.code}
```

**Exception Hierarchy:**
```python
class MCPError(Exception):
    """Base exception for all MCP errors."""
    
    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict | None = None,
    ):
        self.message = message
        self.code = code or "UNKNOWN"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Serialize for error responses."""
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details,
        }

class ValidationError(MCPError):
    """Input validation failed."""
    code = "VALIDATION_ERROR"

class DatabaseError(MCPError):
    """Database operation failed."""
    code = "DATABASE_ERROR"

class TimeoutError(MCPError):
    """Operation timed out."""
    code = "TIMEOUT"

class ToolExecutionError(MCPError):
    """Tool execution failed."""
    code = "TOOL_EXECUTION_FAILED"
```

---

## Usage in MCPs

### Example: forensic-mcp Integration

**Step 1: Add to pyproject.toml**

```toml
[project]
name = "forensic-mcp"
version = "0.1.0"
dependencies = [
    "cybersecsuite-mcp-core==0.1.0",
    "mcp>=0.1.0",
]
```

**Step 2: Use in models**

```python
# forensic_mcp/models.py
from cybersecsuite_mcp_core.db import BaseModel, CharField, IntField, DatetimeField
from cybersecsuite_mcp_core.validation import Artifact, IOC

class AnalysisRecord(BaseModel):
    id = IntField(pk=True)
    artifact_path = CharField(max_length=1024)
    analysis_result = CharField(max_length=10000)
    iocs_found = IntField(default=0)
    
    class Meta:
        table = "forensic_analysis_records"
```

**Step 3: Use logging and caching**

```python
# forensic_mcp/analyzer.py
from cybersecsuite_mcp_core.logging import get_logger, log_context
from cybersecsuite_mcp_core.cache import cached
from cybersecsuite_mcp_core.validation import AnalysisResult, IOC
from cybersecsuite_mcp_core.scope import current_scope

logger = get_logger(__name__)

@cached(ttl=3600, key_prefix="forensic")
async def analyze_artifact(artifact_path: str) -> AnalysisResult:
    """Analyze artifact with caching and logging."""
    
    scope = current_scope()
    with log_context(investigation=scope.investigation_id):
        logger.info("Starting artifact analysis", extra={"path": artifact_path})
        
        try:
            # Perform analysis
            iocs = await extract_iocs(artifact_path)
            
            return AnalysisResult(
                status="success",
                iocs=[IOC(type=ioc["type"], value=ioc["value"]) for ioc in iocs],
                execution_time_ms=1234.5,
            )
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise ToolExecutionError(
                message="Artifact analysis failed",
                details={"artifact": artifact_path, "error": str(e)},
            )
```

**Step 4: Startup initialization**

```python
# forensic_mcp/main.py
import asyncio
from cybersecsuite_mcp_core.db import get_db_connection, create_tables
from cybersecsuite_mcp_core.logging import setup_logging
from forensic_mcp.models import AnalysisRecord

async def startup():
    # Set up logging
    setup_logging(
        app_name="forensic-mcp",
        level="INFO",
        json_format=True,
    )
    
    # Set up database
    await get_db_connection(
        db_url="postgres://user:pass@localhost/cybersecsuite",
        modules=["forensic_mcp.models"],
    )
    await create_tables()

async def shutdown():
    from cybersecsuite_mcp_core.db import close_db_connection
    await close_db_connection()

if __name__ == "__main__":
    asyncio.run(startup())
    # Run MCP server...
```

---

## Versioning Strategy

### Synchronization Rule
**All 12 MCPs must pin to the same core package version:**

```toml
# forensic-mcp/pyproject.toml
dependencies = ["cybersecsuite-mcp-core==0.1.0"]

# purple-team-mcp/pyproject.toml
dependencies = ["cybersecsuite-mcp-core==0.1.0"]

# (all 12 MCPs)
```

### Release Process

| Step | Actor | When |
|------|-------|------|
| 1 | Core maintainer | Develop feature/fix in core package |
| 2 | Core maintainer | Bump version: 0.1.0 → 0.1.1 (patch) |
| 3 | Core maintainer | Publish to PyPI: `uv publish` |
| 4 | Release manager | Create issue: "Update core to v0.1.1" |
| 5 | Each MCP maintainer | Update pyproject.toml dependency, test, merge PR |
| 6 | Release manager | Coordinate simultaneous release of all 12 MCPs |

### Backward Compatibility

**Strategy:** Semantic versioning with deprecation window.

```python
# Example: Deprecating cache.set() parameters

# core/cache.py - Version 0.1.0
def set(self, key: str, value: Any, ttl: int) -> None:
    ...

# core/cache.py - Version 0.2.0 (with deprecation)
def set(
    self, 
    key: str, 
    value: Any, 
    ttl: int | None = None,
    ttl_seconds: int | None = None,  # New param
) -> None:
    if ttl is not None and ttl_seconds is not None:
        raise ValueError("Cannot specify both ttl and ttl_seconds")
    
    if ttl is not None:
        logger.warning("Parameter 'ttl' deprecated, use 'ttl_seconds'")
        actual_ttl = ttl
    else:
        actual_ttl = ttl_seconds or 3600
    
    ...

# core/cache.py - Version 0.3.0 (remove deprecated param)
def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
    ...
```

**MCPs must update before deprecation deadline:**
- Deprecation announced: Version X.Y.Z
- Warning logged: Version X.Y.Z through X+1.Y.Z
- Removed: Version X+1.0.0

---

## Maintenance Process

### Updating Core Package

**Common tasks:**

```bash
# 1. Make changes to src/cybersecsuite_mcp_core/
vim src/cybersecsuite_mcp_core/cache.py

# 2. Write/update tests
pytest tests/test_cache.py -v

# 3. Bump version
# Edit: pyproject.toml version = "0.1.1"

# 4. Publish
uv publish --token $PYPI_TOKEN

# 5. Create update issue for all MCPs
# (Tool: GitHub issue template)
```

### Propagating Changes to MCPs

**Automation script (in CyberSecSuite):**

```bash
#!/bin/bash
# scripts/update_mcp_core.sh <new_version>

NEW_VERSION=$1
MCP_REPOS=(
    "dcx7c5/forensic-mcp"
    "dcx7c5/purple-team-mcp"
    "dcx7c5/encoding-specialist-mcp"
    # ... 9 more
)

for repo in "${MCP_REPOS[@]}"; do
    echo "Updating $repo to core v$NEW_VERSION"
    
    # Clone (or fetch if exists)
    if [ -d "/tmp/$repo" ]; then
        cd "/tmp/$repo"
        git pull
    else
        git clone "https://github.com/$repo"
        cd "/tmp/$repo"
    fi
    
    # Update dependency
    sed -i "s/cybersecsuite-mcp-core==[0-9.]*/cybersecsuite-mcp-core==$NEW_VERSION/" pyproject.toml
    
    # Test
    pytest tests/ -v || exit 1
    
    # Commit and push
    git add pyproject.toml
    git commit -m "Update core to v$NEW_VERSION"
    git push origin main
done
```

### Testing Compatibility

**Before propagating updates:**

```bash
# Test core changes against all MCPs

# 1. Install core locally (dev mode)
cd packages/cybersecsuite_mcp_core
pip install -e .

# 2. For each MCP, run tests
for mcp in forensic-mcp purple-team-mcp encoding-specialist-mcp; do
    cd ~/src/$mcp
    pip install -e .  # Install MCP with new core
    pytest tests/ -v || exit 1
    echo "✓ $mcp passed"
done

echo "All MCPs compatible with core changes"
```

---

## Summary

| Aspect | Decision |
|--------|----------|
| **Package name** | `cybersecsuite_mcp_core` (PyPI) |
| **Initial version** | 0.1.0 (Phase 1) |
| **Versioning** | All MCPs pin to ==X.Y.Z (synchronized) |
| **Release** | Coordinate core bump + all 12 MCP updates |
| **Deprecation** | 2-version warning window before removal |
| **Python** | >=3.9 (match FastAPI/async requirements) |
| **Key modules** | db, cache, validation, logging, scope, exceptions |
| **Distribution** | PyPI + wheel format |

This design ensures 12 independent MCPs share infrastructure without version conflicts or maintenance burden.
