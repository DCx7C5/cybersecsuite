"""Logging configuration with lazy initialization."""


import logging
import logging.handlers
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

_loggers: dict[str, logging.Logger] = {}


def _get_log_level() -> int:
    from css.core.settings.config import LOG_LEVEL

    level_name = str(LOG_LEVEL).upper()
    return getattr(logging, level_name, logging.INFO)


def _ensure_root() -> logging.Logger:
    """Lazily configure root logger (runs once on first getLogger call)."""
    if "cybersecsuite" in _loggers:
        return _loggers["cybersecsuite"]

    from css.core.settings.config import (
        LOG_DATE_FORMAT,
        LOG_FILE_BACKUP_COUNT,
        LOG_FILE_MAX_BYTES,
        LOG_FILE_PATH,
        LOG_FORMAT,
        LOG_TO_FILE,
        LOG_TO_STDOUT,
    )

    log_level = _get_log_level()
    root = logging.getLogger("cybersecsuite")
    root.setLevel(log_level)
    root.propagate = False

    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
    )

    if LOG_TO_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=LOG_FILE_PATH,
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_FILE_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    if LOG_TO_STDOUT:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        root.addHandler(stream_handler)

    _loggers["cybersecsuite"] = root

    return root


def getLogger(name: str) -> Logger:
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
    log_level = _get_log_level()
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    _loggers[name] = logger
    return logger
