#!/usr/bin/env python3
"""
uvloop integration for high-performance async operations.

Provides drop-in replacement for asyncio event loop with significant
performance improvements for I/O intensive cybersecurity operations.
"""
import asyncio
import os
import sys
import logging

try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False
    uvloop = None

logger = logging.getLogger(__name__)


def install_uvloop():
    """Install uvloop as the default event loop policy if available."""
    if not UVLOOP_AVAILABLE:
        logger.warning("uvloop not available, falling back to default asyncio loop")
        return False

    if sys.platform == 'win32':
        logger.warning("uvloop not supported on Windows, using default asyncio loop")
        return False

    try:
        uvloop.install()
        logger.info("✅ uvloop installed as default event loop - expect 2-4x async performance boost")
        return True
    except Exception as e:
        logger.error(f"Failed to install uvloop: {e}")
        return False


def create_uvloop():
    """Create a uvloop event loop instance."""
    if not UVLOOP_AVAILABLE or sys.platform == 'win32':
        return asyncio.new_event_loop()

    try:
        return uvloop.new_event_loop()
    except Exception as e:
        logger.error(f"Failed to create uvloop: {e}")
        return asyncio.new_event_loop()


def run_with_uvloop(coro):
    """Run coroutine with uvloop if available, otherwise default asyncio."""
    if UVLOOP_AVAILABLE and sys.platform != 'win32':
        return uvloop.run(coro)

    return asyncio.run(coro)


def get_event_loop_info():
    """Get information about the current event loop."""
    try:
        loop = asyncio.get_running_loop()
        loop_type = type(loop).__name__

        if 'uvloop' in loop_type.lower():
            return {
                "type": "uvloop",
                "class": loop_type,
                "performance": "high",
                "available": True
            }
        else:
            return {
                "type": "asyncio",
                "class": loop_type,
                "performance": "standard",
                "available": UVLOOP_AVAILABLE
            }
    except RuntimeError:
        return {
            "type": "none",
            "class": "No running loop",
            "performance": "n/a",
            "available": UVLOOP_AVAILABLE
        }


# Auto-install uvloop on module import (can be disabled by setting env var)
if os.environ.get("CYBERSEC_DISABLE_UVLOOP", "").lower() not in ("1", "true", "yes"):
    install_uvloop()