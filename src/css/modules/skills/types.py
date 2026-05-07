"""Skill types — concrete implementation of BaseSkill with installation tracking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from css.core.types.base_entity import BaseSkill
from css.core.types.headers import BaseSkillHeader


@dataclass
class Skill(BaseSkill):
    """Concrete skills entity with marketplace installation tracking.

    Extends BaseSkill with:
      - Installation status (available, installed, update_available, deprecated)
      - Local installation path
      - Installation timestamp
      - Integration with marketplace registry and loader
    """

    header: BaseSkillHeader | None = None
    status: Literal["available", "installed", "update_available", "deprecated"] = "available"
    install_path: str | None = None
    installed_at: datetime | None = None

    @property
    def is_installed(self) -> bool:
        """Check if this skills is currently installed."""
        return self.status in ("installed", "update_available")

    @property
    def has_update(self) -> bool:
        """Check if an update is available for this skills."""
        return self.status == "update_available"

    @property
    def is_deprecated(self) -> bool:
        """Check if this skills is deprecated."""
        return self.status == "deprecated"
