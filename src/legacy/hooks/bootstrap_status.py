"""Bootstrap status tracking for idempotent OnFirstSetupEvent execution."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

log = logging.getLogger(__name__)

BOOTSTRAP_STATUS_FILE = Path.home() / ".cybersecsuite" / "marketplace" / ".bootstrap_status.json"


@dataclass
class BootstrapStatus:
    """Tracks the state of the bootstrap process to enable recovery."""

    status: Literal["in_progress", "completed", "failed", "resumed"] = "in_progress"
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str | None = None
    failed_at: str | None = None
    failed_reason: str | None = None
    installed_items: list[str] = field(default_factory=list)
    failed_items: dict[str, str] = field(default_factory=dict)
    phase: Literal["reading_globals", "checking_sha512", "downloading_index", "seeding_db", "downloading_items"] = "reading_globals"

    @classmethod
    def load(cls) -> BootstrapStatus | None:
        """Load existing bootstrap status, if any."""
        if not BOOTSTRAP_STATUS_FILE.exists():
            return None
        try:
            data = json.loads(BOOTSTRAP_STATUS_FILE.read_text())
            return cls(**data)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            log.warning(f"Failed to load bootstrap status: {e}")
            return None

    def save(self) -> None:
        """Persist this status to disk."""
        BOOTSTRAP_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        BOOTSTRAP_STATUS_FILE.write_text(json.dumps(asdict(self), indent=2))

    def mark_complete(self) -> None:
        """Mark bootstrap as successfully completed."""
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()
        self.save()

    def mark_failed(self, reason: str) -> None:
        """Mark bootstrap as failed with reason."""
        self.status = "failed"
        self.failed_at = datetime.now().isoformat()
        self.failed_reason = reason
        self.save()

    def record_installed(self, item_id: str) -> None:
        """Record a successfully installed marketplace item."""
        if item_id not in self.installed_items:
            self.installed_items.append(item_id)

    def record_failed(self, item_id: str, reason: str) -> None:
        """Record a failed marketplace item installation."""
        self.failed_items[item_id] = reason

    def advance_phase(self, phase: Literal["reading_globals", "checking_sha512", "downloading_index", "seeding_db", "downloading_items"]) -> None:
        """Move to next bootstrap phase."""
        self.phase = phase
        self.save()

    def is_recoverable(self) -> bool:
        """Check if bootstrap can be resumed from current state."""
        if self.status == "completed":
            return True
        if self.status == "failed" and not self.failed_items:
            return True
        return self.status == "in_progress"

    def clear(self) -> None:
        """Clear the bootstrap status file (for testing or manual reset)."""
        if BOOTSTRAP_STATUS_FILE.exists():
            BOOTSTRAP_STATUS_FILE.unlink()
