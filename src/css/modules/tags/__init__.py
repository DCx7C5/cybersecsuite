"""Tag management and classification."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .manager import TagManager, normalize_slug
from .models import Tag
from .enums import TagColor
from .exceptions import (
    BaseTagException,
    TagNotFoundError,
    TagCreationError,
    TagValidationError,
)

__all__ = [
    # Manager
    "TagManager",
    "normalize_slug",
    
    # Models
    "Tag",
    
    # Enums
    "TagColor",
    
    # Exceptions
    "BaseTagException",
    "TagNotFoundError",
    "TagCreationError",
    "TagValidationError",
]

logger.info("Tags module loaded")

