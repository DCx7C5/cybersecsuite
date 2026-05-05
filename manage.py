#!/usr/bin/env python3
"""CyberSecSuite management CLI.

Usage:
    python manage.py serve [--reload] [--host HOST] [--port PORT]
    python manage.py init-db
    python manage.py check
    uv run python manage.py serve --reload
"""
import sys
from pathlib import Path

# Ensure src/ is on sys.path for direct invocation
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from css.manager import main_sync

if __name__ == "__main__":
    main_sync()
