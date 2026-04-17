"""CyberSecSuite integrity checks — model, fixture, and config consistency."""

from __future__ import annotations

from typing import Any

from checks._constants import (  # noqa: F401 — re-exported for backwards compat
    _SRC_ROOT, _REPO_ROOT, _MODEL_BASES, _RELATIONAL_FIELDS, _SKIP_STEMS,
)
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
