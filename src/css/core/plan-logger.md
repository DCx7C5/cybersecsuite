# @logger — Unified Logging System

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/core/logger.py` (71 lines)

**Responsibility**: Centralized logger factory, lazy root initialization, dual output (file + stdout), cached instances.

---

## Overview

Every module initializes its logger from the core factory:

```python
from css.core.logger import getLogger

logger = getLogger(__name__)  # Lazy initialization on first call
```

**Result**: Logger instances named `css.modules.cache`, `css.modules.chat`, etc.

---

## Implementation Details

**Key feature**: Root logger only initialized on **first `getLogger()` call**

```python
# src/css/core/logger.py (actual implementation)

import logging
import logging.handlers
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASGI_LOG = PROJECT_ROOT / "asgi.log"

_log_level = logging.INFO
_loggers: dict[str, logging.Logger] = {}

def _ensure_root() -> logging.Logger:
    """Lazily configure root logger (runs once on first getLogger call)."""
    global _loggers
    if "cybersecsuite" in _loggers:
        return _loggers["cybersecsuite"]
    
    root = logging.getLogger("cybersecsuite")
    root.setLevel(_log_level)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # File handler (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=ASGI_LOG,
        maxBytes=1024 * 1024,    # 1MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    root.addHandler(file_handler)
    root.addHandler(stream_handler)
    _loggers["cybersecsuite"] = root
    
    return root

def getLogger(name: str) -> logging.Logger:
    """Get a logger instance, cached for reuse.
    
    Args:
        name: Logger name (typically __name__ from calling module)
    
    Returns:
        Configured logger instance
    
    Example:
        from css.core.logger import getLogger
        logger = getLogger(__name__)  # 'css.modules.cache'
        logger.info("Cache hit: key123")
    """
    if name in _loggers:
        return _loggers[name]
    
    _ensure_root()
    logger = logging.getLogger(name)
    logger.setLevel(_log_level)
    _loggers[name] = logger
    return logger
```
---

## Log Levels & Examples

| Level | Example |
|-------|---------|
| `DEBUG` | `logger.debug(f"Cache L1 miss, checking L2")` |
| `INFO` | `logger.info(f"Marketplace seeded: 36 agents")` |
| `WARNING` | `logger.warning(f"Redis timeout, falling back")` |
| `ERROR` | `logger.error(f"Checksum mismatch: {item_id}")` |
| `CRITICAL` | `logger.critical(f"Database unreachable")` |

---

## Output Destinations

### 1. **File Logging**

- **Location**: `src/css/asgi.log` (in project root)
- **Rotating**: 1MB per file, keep 5 backups (5MB total)
- **Format**: ISO timestamp + logger name + level + message

### 2. **Console Logging**

- **Destination**: stdout (captured by Docker daemon)
- **View with**: `docker logs cybersec-proxy`
- **Same format** as file handler

---

## Module Logger Pattern

Every module's `__init__.py` follows this pattern:

```python
"""Module docstring."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)  # Becomes 'css.modules.{module_name}'

from .models import ...
from .exceptions import ...

__all__ = [...]
```

---

## Caching Mechanism

Module loggers are cached in `_loggers` dict:

```python
_loggers = {
    "cybersecsuite": <root logger>,
    "css.modules.marketplace": <marketplace logger>,
    "css.modules.chat": <chat logger>,
    # ... all other module loggers
}
```

Subsequent calls to `getLogger(name)` return cached instance (no re-initialization).

---

## Integration Points

- **All modules**: Import `getLogger` from core.logger
- **Docker**: stdout captured by daemon (logs with `docker logs`)
- **Persistent storage**: `asgi.log` rotates in project root
- **Future**: OpenObserve integration for telemetry

---

**Status**: 🟢 Implemented | **Priority**: 🔴 High | **Last Updated**: 2026-05-03
