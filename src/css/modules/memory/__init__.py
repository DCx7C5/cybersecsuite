"""Working memory and state management."""

from css.core.logger import getLogger

from .canvas.canvas_validate import validate_canvas
from .canvas.generator import CanvasGenerator
from .context_window import ContextWindow, TokenEstimate, WindowConfig
from .enums import MemoryEntryKind, MemoryScope, MemoryTier
from .exceptions import BaseMemoryException, MemoryNotFoundError, MemoryPersistenceError
from .models import MemoryEntryRecord, MemorySnapshotRecord
from .session_store import SessionStore
from .types import MemoryEntry, MemorySnapshot
from .vault.hot_cache import HotCache, HotCacheState
from .vault.manager import VaultManager

logger = getLogger(__name__)

__all__ = [
    "MemoryEntryKind",
    "MemoryScope",
    "MemoryTier",
    "BaseMemoryException",
    "MemoryNotFoundError",
    "MemoryPersistenceError",
    "MemoryEntry",
    "MemorySnapshot",
    "MemoryEntryRecord",
    "MemorySnapshotRecord",
    "HotCache",
    "HotCacheState",
    "VaultManager",
    "CanvasGenerator",
    "validate_canvas",
    "ContextWindow",
    "TokenEstimate",
    "WindowConfig",
    "SessionStore",
]
