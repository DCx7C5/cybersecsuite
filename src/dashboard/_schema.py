"""Model schema introspector for the dashboard generic table endpoint.

Imports all Tortoise ORM models at first use and builds a registry mapping
model name (CamelCase and snake_case) → {table, fields, model_cls, module}.
"""
from __future__ import annotations

import importlib
import re
from typing import Any

from tortoise.models import Model

from db.models import MODEL_MODULES

# ── Registry ─────────────────────────────────────────────────────────────────

_REGISTRY: dict[str, dict[str, Any]] | None = None

# Field types that hold relational FK/M2M — serialised differently
_RELATION_TYPES = frozenset({
    "ForeignKeyFieldInstance",
    "ManyToManyFieldInstance",
    "BackwardsOneToOneRelation",
    "BackwardsFKRelation",
    "OneToOneFieldInstance",
})


def _to_snake(name: str) -> str:
    """Convert CamelCase → snake_case."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s).lower()


def _build_registry() -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for mod_path in MODEL_MODULES:
        try:
            mod = importlib.import_module(mod_path)
        except Exception:
            continue
        for attr_name in dir(mod):
            obj = getattr(mod, attr_name, None)
            if obj is None or attr_name.startswith("_"):
                continue
            try:
                if not (isinstance(obj, type) and issubclass(obj, Model) and obj is not Model):
                    continue
            except TypeError:
                continue
            fields: list[dict[str, str]] = []
            for fname, field in obj._meta.fields_map.items():
                ftype = type(field).__name__
                fields.append({"name": fname, "type": ftype, "is_relation": ftype in _RELATION_TYPES})
            entry: dict[str, Any] = {
                "model_cls": obj,
                "table": obj._meta.db_table,
                "module": mod_path,
                "fields": fields,
                "scalar_fields": [f["name"] for f in fields if not f["is_relation"]],
            }
            registry[attr_name] = entry
            snake = _to_snake(attr_name)
            if snake != attr_name:
                registry[snake] = entry
            # Also register db_table name
            registry[obj._meta.db_table] = entry
    return registry


def get_registry() -> dict[str, dict[str, Any]]:
    """Return (and lazily build) the model registry."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build_registry()
    return _REGISTRY


def list_models() -> list[dict[str, str]]:
    """Return a sorted list of {name, table, field_count} dicts for all models."""
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for key, info in get_registry().items():
        table = info["table"]
        if table in seen:
            continue
        seen.add(table)
        result.append({
            "name": key,
            "table": table,
            "module": info["module"],
            "field_count": len(info["fields"]),
        })
    return sorted(result, key=lambda x: x["name"])


def resolve_model(name: str) -> dict[str, Any] | None:
    """Look up a model by CamelCase name, snake_case, or db_table. Returns None if unknown."""
    return get_registry().get(name)


async def fetch_rows(
    model_cls: type[Model],
    scalar_fields: list[str],
    page: int,
    limit: int,
    sort: str | None,
    filters: dict[str, str],
) -> tuple[list[dict[str, Any]], int]:
    """Query paginated rows from a Tortoise model. Returns (rows, total)."""
    qs = model_cls.all()

    # Apply simple equality filters
    valid_fields = {f for f in scalar_fields}
    safe_filters = {k: v for k, v in filters.items() if k in valid_fields}
    if safe_filters:
        qs = qs.filter(**safe_filters)

    total: int = await qs.count()

    # Sorting
    if sort:
        order = sort.lstrip("-")
        if order in valid_fields:
            qs = qs.order_by(sort)
        else:
            qs = qs.order_by("-id") if "id" in valid_fields else qs
    else:
        qs = qs.order_by("-id") if "id" in valid_fields else qs

    offset = (page - 1) * limit
    rows_qs = qs.offset(offset).limit(limit).values(*scalar_fields)
    raw: list[dict[str, Any]] = await rows_qs

    # Serialise non-JSON-safe values
    serialised: list[dict[str, Any]] = []
    for row in raw:
        clean: dict[str, Any] = {}
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                clean[k] = v.isoformat()
            elif hasattr(v, "value"):  # Enum
                clean[k] = v.value
            else:
                clean[k] = v
        serialised.append(clean)

    return serialised, total
