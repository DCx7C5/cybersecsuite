"""Logging configuration with lazy initialization."""


import logging
import logging.handlers
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

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

    file_handler = logging.handlers.RotatingFileHandler(
        filename=ASGI_LOG, maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(stream_handler)
    _loggers["cybersecsuite"] = root

    return root


def getLogger(name: str) -> "Logger":
    """Get a logger instance, cached for reuse.

    Args:
        name: Logger name (typically __name__ from calling module).

    Returns:
        Configured logger instance.

    Example:
        from logger import getLogger
        logger = getLogger(__name__)
        logger.info("message")
    """
    if name in _loggers:
        return _loggers[name]

    _ensure_root()
    logger = logging.getLogger(name)
    logger.setLevel(_log_level)
    _loggers[name] = logger
    return logger
