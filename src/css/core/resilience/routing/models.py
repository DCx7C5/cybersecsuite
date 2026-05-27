"""Routing combo value models."""

import msgspec

from .strategy import Strategy


class ComboTarget(msgspec.Struct, frozen=True, kw_only=True):
    """A configured provider/model target in a combo definition."""

    provider_id: str
    model_id: str
    weight: float = 1.0
    enabled: bool = True
    metadata: dict[str, object] = msgspec.field(default_factory=dict)


class ComboConfig(msgspec.Struct, frozen=True, kw_only=True):
    """Combo configuration loaded from YAML/DB."""

    id: str
    name: str
    strategy: Strategy
    targets: list[ComboTarget]
    budget_usd: float
    description: str = ""
    tags: list[str] = msgspec.field(default_factory=list)


class ResolvedTarget(msgspec.Struct, frozen=True, kw_only=True):
    """Runtime-resolved target for routing execution."""

    provider: str
    model_id: str
    weight: float = 1.0
    enabled: bool = True
    combo_id: str = ""
    tier_name: str = ""
    metadata: dict[str, object] = msgspec.field(default_factory=dict)
