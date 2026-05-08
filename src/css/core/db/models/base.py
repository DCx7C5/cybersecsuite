"""Shared abstract base model for Tortoise ORM entities."""
from tortoise.fields import BigIntField
from tortoise.models import Model



class BaseModel(Model):
    """Canonical ORM base class for the project."""

    id = BigIntField(primary_key=True)

    class Meta:
        abstract = True


# TODO: Improve BaseModel