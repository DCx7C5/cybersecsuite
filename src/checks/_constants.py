"""Shared constants for all integrity-check sub-modules."""
from __future__ import annotations

import ast  # noqa: F401 — imported here so sub-modules can rely on it via star-import
from pathlib import Path

# Root paths resolved relative to this file (works from any cwd).
_SRC_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _SRC_ROOT.parent

# Tortoise ORM model base class names.
_MODEL_BASES = frozenset({"Model", "ScopedEntry"})

# Tortoise ORM relational field constructors.
_RELATIONAL_FIELDS = frozenset({
    "ForeignKeyField",
    "ManyToManyField",
    "OneToOneField",
})

# db/models files that contain no Model subclasses.
_SKIP_STEMS = frozenset({"__init__", "enums", "permission_checker"})

