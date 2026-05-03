"""Abstract base classes for marketplace items using @dataclass."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict

from .enums import MarketplaceItemType, MarketplaceItemStatus


class BaseMarketplaceItem(ABC):
    """Abstract base for ALL marketplace items (agents, skills, combos, templates)."""

    def __init__(self, id: str, name: str, description: str, kind: MarketplaceItemType,
                 version: str = "0.1.0", tags: Optional[List[str]] = None,
                 status: MarketplaceItemStatus = MarketplaceItemStatus.disabled,
                 meta: Optional[Dict] = None):
        self.id = id
        self.name = name
        self.description = description
        self.kind = kind
        self.version = version
        self.tags = tags or []
        self.status = status
        self.meta = meta or {}

    @abstractmethod
    def get_install_path(self) -> Optional[str]:
        """Return the installation path, or None if not installed."""
        ...

    @abstractmethod
    def validate(self) -> tuple[bool, List[str]]:
        """Validate the item. Returns (is_valid, list_of_errors)."""
        ...


class BaseInstallable(BaseMarketplaceItem, ABC):
    """Abstract base for installable marketplace items."""

    def __init__(self, id: str, name: str, description: str, kind: MarketplaceItemType,
                 version: str = "0.1.0", tags: Optional[List[str]] = None,
                 status: MarketplaceItemStatus = MarketplaceItemStatus.disabled,
                 meta: Optional[Dict] = None,
                 source_url: Optional[str] = None,
                 install_path: Optional[str] = None,
                 installed_at: Optional[datetime] = None):
        super().__init__(id, name, description, kind, version, tags, status, meta)
        self.source_url = source_url
        self.install_path = install_path
        self.installed_at = installed_at

    def is_installed(self) -> bool:
        """Check if item is installed."""
        return self.installed_at is not None

    def get_install_path(self) -> Optional[str]:
        return self.install_path

    @abstractmethod
    async def install(self, force: bool = False) -> Dict:
        """Install the item. Returns InstallationResult dict."""
        ...

    @abstractmethod
    async def uninstall(self) -> Dict:
        """Uninstall the item. Returns UninstallationResult dict."""
        ...


class BaseToggleable(BaseInstallable, ABC):
    """Abstract base for items that can be enabled/disabled."""

    def __init__(self, id: str, name: str, description: str, kind: MarketplaceItemType,
                 version: str = "0.1.0", tags: Optional[List[str]] = None,
                 status: MarketplaceItemStatus = MarketplaceItemStatus.disabled,
                 meta: Optional[Dict] = None,
                 source_url: Optional[str] = None,
                 install_path: Optional[str] = None,
                 installed_at: Optional[datetime] = None,
                 enabled: bool = False):
        super().__init__(id, name, description, kind, version, tags, status, meta, source_url, install_path, installed_at)
        self.enabled = enabled

    @abstractmethod
    async def toggle(self, enabled: bool) -> Dict:
        """Toggle enabled state. Returns ToggleResponse dict."""
        ...