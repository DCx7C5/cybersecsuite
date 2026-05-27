"""ComboRegistry — startup-loaded combo definitions."""

from pathlib import Path
from typing import Any

import yaml

from .models import ComboConfig, ComboTarget
from .strategy import Strategy


class ComboRegistry:
    """Startup-loaded combo configuration memory."""

    def __init__(self) -> None:
        self._combos: dict[str, ComboConfig] = {}

    def load_from_yaml(self, path: str | Path) -> None:
        """Load combo definitions from a YAML file."""
        p = Path(path)
        if not p.is_file():
            return

        raw = p.read_text(encoding="utf-8")
        data: dict[str, Any] = yaml.safe_load(raw) or {}
        for entry in data.get("combos", []):
            try:
                combo = _yaml_to_combo(entry)
                self._combos[combo.id] = combo
            except Exception:
                continue

    async def load_from_db(self) -> None:
        """Load user-defined combos from the database (best-effort)."""
        try:
            import importlib
            combo_mod = importlib.import_module("css.core.db.models.combo")
            ComboDefinition = combo_mod.ComboDefinition

            for record in await ComboDefinition.all():
                try:
                    targets = [
                        ComboTarget(
                            provider_id=t.get("provider_id", ""),
                            model_id=t.get("model_id", ""),
                            weight=float(t.get("weight", 1.0)),
                            enabled=bool(t.get("enabled", True)),
                            metadata=t.get("metadata", {}),
                        )
                        for t in (record.targets or [])
                    ]
                    self._combos[record.combo_id] = ComboConfig(
                        id=record.combo_id,
                        name=record.name,
                        strategy=Strategy(record.strategy),
                        targets=targets,
                        budget_usd=record.budget_usd,
                        description=record.description or "",
                        tags=list(record.tags or []),
                    )
                except Exception:
                    continue
        except ImportError:
            pass
        except Exception:
            pass

    def get(self, combo_id: str) -> ComboConfig | None:
        return self._combos.get(combo_id)

    def list_all(self) -> list[ComboConfig]:
        return list(self._combos.values())

    def invalidate(self, combo_id: str | None = None) -> None:
        if combo_id is not None:
            self._combos.pop(combo_id, None)
        else:
            self._combos.clear()

    def handle_combo_saved(self, combo_id: str) -> None:
        self.invalidate(combo_id)


def _yaml_to_combo(entry: dict[str, Any]) -> ComboConfig:
    targets = []
    for t in entry.get("targets", []):
        targets.append(
            ComboTarget(
                provider_id=t["provider_id"],
                model_id=t["model_id"],
                weight=float(t.get("weight", 1.0)),
                enabled=bool(t.get("enabled", True)),
                metadata=t.get("metadata", {}),
            )
        )
    return ComboConfig(
        id=entry["id"],
        name=entry.get("name", entry["id"]),
        strategy=Strategy(entry["strategy"]),
        targets=targets,
        budget_usd=float(entry.get("budget_usd", 0.0)),
        description=entry.get("description", ""),
        tags=entry.get("tags", []),
    )


combo_registry: ComboRegistry = ComboRegistry()
