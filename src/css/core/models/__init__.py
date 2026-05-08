"""LLM model registry and management."""

from .enums import ModelProvider, ModelFamily, ModelCapability
from .models import ModelMetadata, ModelPricing
from .registry import ModelRegistry, DEFAULT_MODELS

from css.core.logger import getLogger
logger = getLogger(__name__)

__all__ = [
    # Enums
    "ModelProvider",
    "ModelFamily",
    "ModelCapability",
    
    # Models
    "ModelMetadata",
    "ModelPricing",
    
    # Registry
    "ModelRegistry",
    "DEFAULT_MODELS",
]

logger.info("LLM models module loaded")
