from typing import Generic, TypeVar

from models import BaseModel


ModelType = TypeVar("ModelType", bound="BaseModel")



class BaseManager(Generic[ModelType]):
    """Base class for model managers providing common query patterns.

    Subclasses should be instantiated and assigned to model.manager in concrete ORM models.
    Provides async query helpers for common operations like filtering by active status.
    """

