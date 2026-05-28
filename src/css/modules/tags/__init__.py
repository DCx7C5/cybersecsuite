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

logger.info("Tags module loaded")
