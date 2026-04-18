#!/usr/bin/env python3
"""
CyberSec management script — thin shim for direct invocation.

Use `python src/manage.py <cmd>` or `uv run python -m manage <cmd>`.
The actual logic lives in src/manage/__init__.py.
"""

import sys
from pathlib import Path

# Ensure src/ is on sys.path when this file is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from manage import _run_main  # noqa: E402

if __name__ == "__main__":
    _run_main()
