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

def check_models() -> list[dict[str, str]]:
    """Programmatically inspect all model FK and M2M references for consistency.

    Checks performed:
      - FK/M2M target model strings (e.g. ``"models.CVEIntel"``) resolve to an
        actual model class defined in the codebase.
      - No duplicate ``Meta.table`` names across model files.
      - No duplicate class names that would collide in the Tortoise registry.
      - No duplicate ``related_name`` values on the same FK target model.
      - Model modules listed in ``MODEL_MODULES`` but with empty source files.

    Returns:
        List of finding dicts with keys ``level``, ``check``, and ``message``.
    """
    findings: list[dict[str, str]] = []
    models_dir = _SRC_ROOT / "db" / "models"

    # Accumulators -----------------------------------------------------------
    # class_name -> [file_stem, ...]
    known_classes: dict[str, list[str]] = {}
    # table_name -> [(file_stem, class_name), ...]
    table_map: dict[str, list[tuple[str, str]]] = {}
    # (target_model_str, related_name) -> [(file_stem, class_name, field), ...]
    rn_map: dict[tuple[str, str], list[tuple[str, str, str]]] = {}
    # All FK/M2M refs: (target_model_str, file_stem, class_name, field_name)
    fk_refs: list[tuple[str, str, str, str]] = []
    # Empty .py files that still appear in MODEL_MODULES
    empty_modules: list[str] = []

    # ── Parse every model file ─────────────────────────────────────────────
    for py_file in sorted(models_dir.glob("*.py")):
        stem = py_file.stem
        if stem in _SKIP_STEMS or stem.startswith("__"):
            continue

        source = py_file.read_text()
        if not source.strip():
            empty_modules.append(stem)
            continue

        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError as exc:
            findings.append({
                "level": "error",
                "check": "models",
                "message": f"Syntax error in {py_file.name}: {exc}",
            })
            continue

        _extract_model_info(
            tree, stem, known_classes, table_map, rn_map, fk_refs, findings,
        )

    # ── Empty modules registered in MODEL_MODULES ──────────────────────────
    registered_stems = _read_model_modules(models_dir / "__init__.py")
    for mod in empty_modules:
        if mod in registered_stems:
            findings.append({
                "level": "warning",
                "check": "models",
                "message": (
                    f"Module db.models.{mod} is registered in MODEL_MODULES "
                    f"but source file is empty (0 bytes)"
                ),
            })

    # ── Duplicate class names ──────────────────────────────────────────────
    for cls_name, files in sorted(known_classes.items()):
        if len(files) > 1:
            locations = ", ".join(f"{f}.py" for f in files)
            findings.append({
                "level": "error",
                "check": "models",
                "message": (
                    f"Duplicate model class '{cls_name}' defined in: {locations}"
                ),
            })

    # ── Duplicate table names ──────────────────────────────────────────────
    for table, entries in sorted(table_map.items()):
        if len(entries) > 1:
            locations = ", ".join(f"{f}.py:{c}" for f, c in entries)
            findings.append({
                "level": "error",
                "check": "models",
                "message": f"Duplicate table name '{table}' in: {locations}",
            })

    # ── Unresolved FK/M2M target model strings ─────────────────────────────
    all_class_names = set(known_classes)
    for target, file_stem, cls_name, field_name in fk_refs:
        # "models.CVEIntel" → "CVEIntel"
        model_name = target.rsplit(".", 1)[-1]
        if model_name not in all_class_names:
            findings.append({
                "level": "error",
                "check": "models",
                "message": (
                    f"FK target '{target}' in {file_stem}.py:{cls_name}.{field_name} "
                    f"does not resolve to any known model class"
                ),
            })

    # ── Duplicate related_name on the same target model ────────────────────
    for (target, rn), entries in sorted(rn_map.items()):
        if len(entries) > 1:
            locations = ", ".join(f"{f}.py:{c}.{fn}" for f, c, fn in entries)
            findings.append({
                "level": "error",
                "check": "models",
                "message": (
                    f"Duplicate related_name '{rn}' on target '{target}' "
                    f"from: {locations}"
                ),
            })

    return findings


# ═══════════════════════════════════════════════════════════════════════════
# check_fixtures
# ═══════════════════════════════════════════════════════════════════════════

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

def check_config() -> list[dict[str, str]]:
    """Verify config file consistency across mcp.json, docker-compose, settings.

    Checks:
      - ``mcp.json``: referenced Python files / modules exist on disk.
      - ``docker-compose.yml``: referenced Dockerfiles exist.
      - ``.claude/settings.json``: ASGI port numbers match docker-compose
        exposed ports.
      - ``pyproject.toml``: declared entry-point modules resolve.

    Returns:
        List of finding dicts with keys ``level``, ``check``, and ``message``.
    """
    findings: list[dict[str, str]] = []
    _check_mcp_json(findings)
    _check_docker_compose(findings)
    _check_settings_ports(findings)
    _check_pyproject_entrypoints(findings)
    return findings


# ═══════════════════════════════════════════════════════════════════════════
# run_all_checks
# ═══════════════════════════════════════════════════════════════════════════

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

def _read_model_modules(init_path: Path) -> set[str]:
    """Read ``MODEL_MODULES`` from ``db/models/__init__.py`` → set of stems."""
    stems: set[str] = set()
    if not init_path.exists():
        return stems
    try:
        tree = ast.parse(init_path.read_text())
    except SyntaxError:
        return stems
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val: str = node.value
            if val.startswith("db.models."):
                stems.add(val.removeprefix("db.models."))
    return stems


def _extract_model_info(
    tree: ast.Module,
    file_stem: str,
    known_classes: dict[str, list[str]],
    table_map: dict[str, list[tuple[str, str]]],
    rn_map: dict[tuple[str, str], list[tuple[str, str, str]]],
    fk_refs: list[tuple[str, str, str, str]],
    findings: list[dict[str, str]],
) -> None:
    """Walk an AST and extract model classes, table names, and FK/M2M fields."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Is this a Model subclass?
        if not any(
            (isinstance(b, ast.Name) and b.id in _MODEL_BASES)
            or (isinstance(b, ast.Attribute) and b.attr in _MODEL_BASES)
            for b in node.bases
        ):
            continue

        cls_name = node.name

        # Check Meta for abstract flag and table name.
        is_abstract = False
        for item in node.body:
            if isinstance(item, ast.ClassDef) and item.name == "Meta":
                for meta_stmt in item.body:
                    if not isinstance(meta_stmt, ast.Assign):
                        continue
                    for tgt in meta_stmt.targets:
                        if not isinstance(tgt, ast.Name):
                            continue
                        if (
                            tgt.id == "abstract"
                            and isinstance(meta_stmt.value, ast.Constant)
                            and meta_stmt.value.value is True
                        ):
                            is_abstract = True
                        elif (
                            tgt.id == "table"
                            and isinstance(meta_stmt.value, ast.Constant)
                            and isinstance(meta_stmt.value.value, str)
                        ):
                            table_map.setdefault(meta_stmt.value.value, []).append(
                                (file_stem, cls_name)
                            )

        if is_abstract:
            continue

        known_classes.setdefault(cls_name, []).append(file_stem)

        # Scan field assignments for FK/M2M/O2O.
        for item in node.body:
            _process_field_assignment(
                item, file_stem, cls_name, fk_refs, rn_map,
            )


def _process_field_assignment(
    item: ast.stmt,
    file_stem: str,
    cls_name: str,
    fk_refs: list[tuple[str, str, str, str]],
    rn_map: dict[tuple[str, str], list[tuple[str, str, str]]],
) -> None:
    """Extract FK/M2M info from a single assignment statement."""
    field_names: list[str] = []
    value: ast.expr | None = None

    if isinstance(item, ast.Assign):
        value = item.value
        field_names = [t.id for t in item.targets if isinstance(t, ast.Name)]
    elif isinstance(item, ast.AnnAssign) and item.value is not None:
        value = item.value
        if isinstance(item.target, ast.Name):
            field_names = [item.target.id]

    if not value or not field_names or not isinstance(value, ast.Call):
        return

    # Identify the field constructor name.
    func = value.func
    field_type: str | None = None
    if isinstance(func, ast.Attribute) and func.attr in _RELATIONAL_FIELDS:
        field_type = func.attr
    elif isinstance(func, ast.Name) and func.id in _RELATIONAL_FIELDS:
        field_type = func.id
    if field_type is None:
        return

    # First positional arg is the model reference string.
    target_model: str | None = None
    if value.args and isinstance(value.args[0], ast.Constant):
        raw = value.args[0].value
        if isinstance(raw, str):
            target_model = raw

    # related_name keyword (skip False / empty).
    related_name: str | None = None
    for kw in value.keywords:
        if kw.arg == "related_name" and isinstance(kw.value, ast.Constant):
            rn_val = kw.value.value
            if rn_val is not False and rn_val:
                related_name = str(rn_val)

    for fn in field_names:
        if target_model:
            fk_refs.append((target_model, file_stem, cls_name, fn))
            if related_name:
                rn_map.setdefault((target_model, related_name), []).append(
                    (file_stem, cls_name, fn)
                )


def _get_meta_table(cls_node: ast.ClassDef) -> str | None:
    """Return the ``Meta.table`` string for a ClassDef, or None."""
    for item in cls_node.body:
        if isinstance(item, ast.ClassDef) and item.name == "Meta":
            for meta_stmt in item.body:
                if isinstance(meta_stmt, ast.Assign):
                    for tgt in meta_stmt.targets:
                        if (
                            isinstance(tgt, ast.Name)
                            and tgt.id == "table"
                            and isinstance(meta_stmt.value, ast.Constant)
                            and isinstance(meta_stmt.value.value, str)
                        ):
                            return meta_stmt.value.value
    return None


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


# ── Config sub-checks ─────────────────────────────────────────────────────

def _check_mcp_json(findings: list[dict[str, str]]) -> None:
    """Verify mcp.json server command paths exist on disk."""
    mcp_path = _REPO_ROOT / "mcp.json"
    if not mcp_path.exists():
        findings.append({
            "level": "error",
            "check": "config",
            "message": "mcp.json not found at repository root",
        })
        return

    try:
        data = json.loads(mcp_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        findings.append({
            "level": "error",
            "check": "config",
            "message": f"Cannot parse mcp.json: {exc}",
        })
        return

    servers = data.get("mcpServers", {})
    for name, cfg in servers.items():
        args: list[str] = cfg.get("args", [])
        # Resolve ${workspaceFolder} → repo root.
        resolved = [a.replace("${workspaceFolder}", str(_REPO_ROOT)) for a in args]

        # Check --directory paths.
        for i, arg in enumerate(resolved):
            if arg == "--directory" and i + 1 < len(resolved):
                dir_path = Path(resolved[i + 1])
                if not dir_path.is_dir():
                    findings.append({
                        "level": "error",
                        "check": "config",
                        "message": (
                            f"mcp.json server '{name}': --directory path "
                            f"'{resolved[i + 1]}' does not exist"
                        ),
                    })

        # Check if referenced Python files exist.
        for arg in resolved:
            if arg.endswith(".py") and not arg.startswith("-"):
                py_path = Path(arg)
                if not py_path.is_absolute():
                    # Relative to the --directory or repo root.
                    dir_idx = None
                    for j, a in enumerate(resolved):
                        if a == "--directory" and j + 1 < len(resolved):
                            dir_idx = j + 1
                            break
                    base = Path(resolved[dir_idx]) if dir_idx is not None else _REPO_ROOT
                    py_path = base / arg
                if not py_path.exists():
                    findings.append({
                        "level": "warning",
                        "check": "config",
                        "message": (
                            f"mcp.json server '{name}': Python file "
                            f"'{arg}' not found on disk"
                        ),
                    })


def _check_docker_compose(findings: list[dict[str, str]]) -> None:
    """Verify Dockerfiles referenced in docker-compose.yml exist."""
    dc_path = _REPO_ROOT / "docker-compose.yml"
    if not dc_path.exists():
        findings.append({
            "level": "warning",
            "check": "config",
            "message": "docker-compose.yml not found at repository root",
        })
        return

    content = dc_path.read_text()

    # Extract build context + dockerfile pairs via regex (avoids pyyaml for
    # x-anchors which stdlib yaml doesn't handle).
    # Pattern: context: <path> ... dockerfile: <path>
    build_blocks = re.findall(
        r"build:\s*\n\s+context:\s*(.+?)\s*\n\s+dockerfile:\s*(.+)",
        content,
    )

    for context, dockerfile in build_blocks:
        context = context.strip()
        dockerfile = dockerfile.strip()
        if context == ".":
            full_path = _REPO_ROOT / dockerfile
        else:
            full_path = _REPO_ROOT / context / dockerfile
        if not full_path.exists():
            findings.append({
                "level": "error",
                "check": "config",
                "message": (
                    f"docker-compose.yml: Dockerfile not found: "
                    f"{full_path.relative_to(_REPO_ROOT)}"
                ),
            })


def _check_settings_ports(findings: list[dict[str, str]]) -> None:
    """Verify .claude/settings.json ports match docker-compose exposed ports."""
    settings_path = _REPO_ROOT / ".claude" / "settings.json"
    dc_path = _REPO_ROOT / "docker-compose.yml"

    if not settings_path.exists() or not dc_path.exists():
        return

    try:
        settings = json.loads(settings_path.read_text())
    except (json.JSONDecodeError, OSError):
        findings.append({
            "level": "warning",
            "check": "config",
            "message": "Cannot parse .claude/settings.json",
        })
        return

    # Extract ASGI ports from settings.
    asgi = settings.get("asgi", {})
    settings_ports: set[int] = set()
    for key in ("port", "alt_port", "tls_port"):
        val = asgi.get(key)
        if isinstance(val, int):
            settings_ports.add(val)

    if not settings_ports:
        return

    # Extract exposed ports from docker-compose.
    dc_content = dc_path.read_text()
    dc_ports: set[int] = set()
    for match in re.finditer(r'"[\d.]+:(\d+):\d+"', dc_content):
        dc_ports.add(int(match.group(1)))

    missing = settings_ports - dc_ports
    for port in sorted(missing):
        findings.append({
            "level": "warning",
            "check": "config",
            "message": (
                f".claude/settings.json declares ASGI port {port} "
                f"but it is not exposed in docker-compose.yml"
            ),
        })


def _check_pyproject_entrypoints(findings: list[dict[str, str]]) -> None:
    """Verify pyproject.toml entry-point modules resolve to files in src/."""
    pyproject_path = _REPO_ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        findings.append({
            "level": "warning",
            "check": "config",
            "message": "pyproject.toml not found at repository root",
        })
        return

    content = pyproject_path.read_text()

    # Parse [project.scripts] entries: name = "module:func"
    in_scripts = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[project.scripts]":
            in_scripts = True
            continue
        if in_scripts:
            if stripped.startswith("["):
                break  # new section
            match = re.match(r'(\S+)\s*=\s*"([^"]+)"', stripped)
            if not match:
                continue
            ep_name, ep_ref = match.group(1), match.group(2)
            # ep_ref is "module.path:function"
            if ":" not in ep_ref:
                continue
            module_part, func_name = ep_ref.rsplit(":", 1)
            module_path = _SRC_ROOT / module_part.replace(".", "/")

            # Could be a package (__init__.py) or a file (.py).
            candidates = [
                module_path.with_suffix(".py"),
                module_path / "__init__.py",
            ]
            if not any(c.exists() for c in candidates):
                findings.append({
                    "level": "error",
                    "check": "config",
                    "message": (
                        f"pyproject.toml entry point '{ep_name}' references "
                        f"module '{module_part}' which cannot be found in src/"
                    ),
                })
                continue

            # Verify the function exists in the module.
            resolved_file = next(c for c in candidates if c.exists())
            try:
                tree = ast.parse(resolved_file.read_text())
            except SyntaxError:
                continue
            func_names = {
                n.name
                for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            if func_name not in func_names:
                findings.append({
                    "level": "error",
                    "check": "config",
                    "message": (
                        f"pyproject.toml entry point '{ep_name}': function "
                        f"'{func_name}' not found in {resolved_file.name}"
                    ),
                })
