"""Shared abstract base model for Tortoise ORM entities."""
from tortoise.fields import BigIntField
from tortoise.models import Model

from ..fields import NameField


# BASEMODEL

class BaseModel(Model):
    """Canonical ORM base class for the project."""

    id = BigIntField(primary_key=True)

    class Meta:
        abstract = True


class BaseUserModel(BaseModel):
    """Abstract base model for user-related entities."""

    username = NameField(max_length=128)

    class Meta:
        abstract = True
