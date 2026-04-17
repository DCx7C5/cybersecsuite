"""CyberSecSuite integrity checks — model, fixture, and config consistency."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Root paths — resolved relative to this file so checks work from any cwd.
# ---------------------------------------------------------------------------
_SRC_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _SRC_ROOT.parent

# Model bases that indicate a Tortoise ORM model class.
_MODEL_BASES = frozenset({"Model", "ScopedEntry"})

# Tortoise ORM relational field constructors we care about.
_RELATIONAL_FIELDS = frozenset({
    "ForeignKeyField",
    "ManyToManyField",
    "OneToOneField",
})

# Files inside db/models/ that contain no Model subclasses.
_SKIP_STEMS = frozenset({"__init__", "enums", "permission_checker"})


# ═══════════════════════════════════════════════════════════════════════════
# check_models
# ═══════════════════════════════════════════════════════════════════════════


from checks._model_check import check_models
from checks._fixture_check import check_fixtures
from checks._config_check import check_config

def run_all_checks() -> dict[str, Any]:
    """Run every integrity check and return a consolidated report.

    Returns:
        Dict with keys ``models``, ``fixtures``, ``config`` (each a list of
        findings), and ``summary`` with ``errors`` and ``warnings`` counts.
    """
    model_findings = check_models()
    fixture_findings = check_fixtures()
    config_findings = check_config()

    all_findings = model_findings + fixture_findings + config_findings
    errors = sum(1 for f in all_findings if f["level"] == "error")
    warnings = sum(1 for f in all_findings if f["level"] == "warning")

    return {
        "models": model_findings,
        "fixtures": fixture_findings,
        "config": config_findings,
        "summary": {
            "errors": errors,
            "warnings": warnings,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════════


__all__ = ['run_all_checks', 'check_models', 'check_fixtures', 'check_config']
