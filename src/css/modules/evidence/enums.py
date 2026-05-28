"""Evidence module enums."""

from enum import Enum


class EvidenceStatus(str, Enum):
    """Evidence lifecycle status."""

    COLLECTED = "collected"
    VERIFIED = "verified"
    SEALED = "sealed"
    ARCHIVED = "archived"
    DESTROYED = "destroyed"


class EvidenceType(str, Enum):
    """Classification of evidence source."""

    LOG_FILE = "log_file"
    NETWORK_CAPTURE = "network_capture"
    DISK_IMAGE = "disk_image"
    MEMORY_DUMP = "memory_dump"
    FILE_SYSTEM = "file_system"
    SYSTEM_STATE = "system_state"
    CONFIG = "config"
    METADATA = "metadata"
    OTHER = "other"


class ChainEventType(str, Enum):
    """Chain-of-custody event types."""

    COLLECTED = "collected"
    TRANSFERRED = "transferred"
    ACCESSED = "accessed"
    VERIFIED = "verified"
    SEALED = "sealed"
    UNSEALED = "unsealed"
    ARCHIVED = "archived"
    RESTORED = "restored"
    DESTROYED = "destroyed"

