"""Model consistency checks."""

from __future__ import annotations

import ast
from pathlib import Path

from a2a.checks._constants import _SRC_ROOT, _SKIP_STEMS, _MODEL_BASES, _RELATIONAL_FIELDS


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
            findings.append(
                {
                    "level": "error",
                    "check": "models",
                    "message": f"Syntax error in {py_file.name}: {exc}",
                }
            )
            continue

        _extract_model_info(
            tree,
            stem,
            known_classes,
            table_map,
            rn_map,
            fk_refs,
            findings,
        )

    # ── Empty modules registered in MODEL_MODULES ──────────────────────────
    registered_stems = _read_model_modules(models_dir / "__init__.py")
    for mod in empty_modules:
        if mod in registered_stems:
            findings.append(
                {
                    "level": "warning",
                    "check": "models",
                    "message": (
                        f"Module db.models.{mod} is registered in MODEL_MODULES "
                        f"but source file is empty (0 bytes)"
                    ),
                }
            )

    # ── Duplicate class names ──────────────────────────────────────────────
    for cls_name, files in sorted(known_classes.items()):
        if len(files) > 1:
            locations = ", ".join(f"{f}.py" for f in files)
            findings.append(
                {
                    "level": "error",
                    "check": "models",
                    "message": (f"Duplicate model class '{cls_name}' defined in: {locations}"),
                }
            )

    # ── Duplicate table names ──────────────────────────────────────────────
    for table, entries in sorted(table_map.items()):
        if len(entries) > 1:
            locations = ", ".join(f"{f}.py:{c}" for f, c in entries)
            findings.append(
                {
                    "level": "error",
                    "check": "models",
                    "message": f"Duplicate table name '{table}' in: {locations}",
                }
            )

    # ── Unresolved FK/M2M target model strings ─────────────────────────────
    all_class_names = set(known_classes)
    for target, file_stem, cls_name, field_name in fk_refs:
        # "models.CVEIntel" → "CVEIntel"
        model_name = target.rsplit(".", 1)[-1]
        if model_name not in all_class_names:
            findings.append(
                {
                    "level": "error",
                    "check": "models",
                    "message": (
                        f"FK target '{target}' in {file_stem}.py:{cls_name}.{field_name} "
                        f"does not resolve to any known model class"
                    ),
                }
            )

    # ── Duplicate related_name on the same target model ────────────────────
    for (target, rn), entries in sorted(rn_map.items()):
        if len(entries) > 1:
            locations = ", ".join(f"{f}.py:{c}.{fn}" for f, c, fn in entries)
            findings.append(
                {
                    "level": "error",
                    "check": "models",
                    "message": (
                        f"Duplicate related_name '{rn}' on target '{target}' from: {locations}"
                    ),
                }
            )

    return findings


# ═══════════════════════════════════════════════════════════════════════════
# check_fixtures
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
                item,
                file_stem,
                cls_name,
                fk_refs,
                rn_map,
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
