"""Tag management and classification."""


from .manager import TagManager, normalize_slug
from .models import Tag
from .enums import TagColor
from .types import TagSuggestion, TagConflictResolution
from css.core.logger import getLogger
from .exceptions import (
    BaseTagException,
    TagNotFoundError,
    TagCreationError,
    TagValidationError,
)

logger = getLogger(__name__)

__all__ = [
    # Manager
    "TagManager",
    "normalize_slug",
    
    # Models
    "Tag",
    
    # Enums
    "TagColor",

    # Types
    "TagSuggestion",
    "TagConflictResolution",
    
    # Exceptions
    "BaseTagException",
    "TagNotFoundError",
    "TagCreationError",
    "TagValidationError",
]

logger.info("Tags module loaded")
