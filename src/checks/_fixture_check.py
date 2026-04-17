"""Fixture coverage checks."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

def check_fixtures() -> list[dict[str, str]]:
    """Check which intel tables have seed fixtures and which do not.

    Scans all model files for ``Meta.table`` values starting with ``"intel_"``
    and compares against JSON files present in ``src/db/fixtures/``.

    Returns:
        List of finding dicts with keys ``level``, ``check``, and ``message``.
    """
    findings: list[dict[str, str]] = []
    models_dir = _SRC_ROOT / "db" / "models"
    fixtures_dir = _SRC_ROOT / "db" / "fixtures"

    # Gather all intel table names and their source classes.
    intel_tables: dict[str, str] = {}  # table_name -> "file:ClassName"
    for py_file in sorted(models_dir.glob("*.py")):
        stem = py_file.stem
        if stem in _SKIP_STEMS or stem.startswith("__"):
            continue
        source = py_file.read_text()
        if not source.strip():
            continue
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            table_name = _get_meta_table(node)
            if table_name and table_name.startswith("intel_"):
                intel_tables[table_name] = f"{stem}.py:{node.name}"

    # Gather available fixture JSON files.
    fixture_files: set[str] = set()
    if fixtures_dir.is_dir():
        fixture_files = {f.stem for f in fixtures_dir.glob("*.json")}

    # Report.
    has_fixture: list[str] = []
    missing_fixture: list[str] = []

    for table, source_loc in sorted(intel_tables.items()):
        # Heuristic: fixture file stem is typically the table name minus "intel_"
        # prefix, or a reasonable variant.  Check multiple candidate names.
        candidates = _fixture_candidates(table)
        matched = candidates & fixture_files
        if matched:
            has_fixture.append(table)
        else:
            missing_fixture.append(table)
            findings.append({
                "level": "warning",
                "check": "fixtures",
                "message": (
                    f"Intel table '{table}' ({source_loc}) has no matching "
                    f"fixture in {fixtures_dir.relative_to(_REPO_ROOT)}/ "
                    f"(tried: {', '.join(sorted(candidates))})"
                ),
            })

    # Summary line.
    findings.append({
        "level": "info" if not missing_fixture else "warning",
        "check": "fixtures",
        "message": (
            f"Intel fixture coverage: {len(has_fixture)}/{len(intel_tables)} "
            f"tables have fixtures, {len(missing_fixture)} missing"
        ),
    })

    return findings


# ═══════════════════════════════════════════════════════════════════════════
# check_config
# ═══════════════════════════════════════════════════════════════════════════

def _fixture_candidates(table_name: str) -> set[str]:
    """Generate plausible fixture file stems for a given table name.

    For ``intel_mitre_techniques`` we try stems like ``mitre_techniques``,
    ``intel_mitre_techniques``, ``mitre_technique_entries``, etc.
    Handles naming divergences like ``intel_mitre_threat_actors`` →
    ``mitre_actors`` and ``intel_capec_patterns`` → ``capec_entries``.
    """
    candidates: set[str] = {table_name}
    # Strip "intel_" prefix.
    bare = table_name.removeprefix("intel_")
    candidates.add(bare)
    # Common naming variants.
    candidates.add(f"{bare}_entries")
    if bare.endswith("s"):
        singular = bare[:-1]
        candidates.add(f"{singular}_entries")
    # Try suffixing "_entries" to the raw table name.
    candidates.add(f"{table_name}_entries")

    # Sub-combinations for multi-word names.
    parts = bare.split("_")
    if len(parts) >= 3:
        # Drop middle word(s): mitre_threat_actors → mitre_actors
        candidates.add(f"{parts[0]}_{parts[-1]}")
        # Drop last word: mitre_software_families → mitre_software
        candidates.add("_".join(parts[:-1]))
    if len(parts) >= 2:
        # Replace last word with "entries": capec_patterns → capec_entries
        candidates.add("_".join(parts[:-1]) + "_entries")

    return candidates


