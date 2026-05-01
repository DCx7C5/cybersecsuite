"""Abstract base context type for conversation and model execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


class BaseContext(ABC):
    """Abstract base for all context types."""
    
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        pass
    
    @abstractmethod
    def update_metadata(self, key: str, value: Any) -> None:
        """Update context metadata."""
        pass


__all__ = ["BaseContext"]
