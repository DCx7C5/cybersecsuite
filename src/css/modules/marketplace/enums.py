from enum import Enum


class MarketplaceStatus(str, Enum):
    """Lifecycle status of a marketplace item."""

    active = "active"
    updates_available = "updates_available"



class MarketplaceItemStatus(str, Enum):
    """Lifecycle status of a marketplace item."""

    installed = "installed"
    update_available = "update_available"
    enabled = "enabled"
    disabled = "disabled"


class MarketplaceItemType(str, Enum):
    """Type of marketplace item."""

    agent = "agent"
    skill = "skill"
    mcp = "mcp"
    template = "template"
    workflow = "workflow"
    prompt = "prompt"
