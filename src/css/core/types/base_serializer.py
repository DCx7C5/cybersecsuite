"""Backward-compatibility shim — base serializer classes live in css.core.db.serializers."""

from css.core.db.serializers import (
    BaseListSerializer,
    BaseModelSerializer,
    BaseSerializer,
    SerializerValidationError,
)

__all__ = [
    "SerializerValidationError",
    "BaseSerializer",
    "BaseModelSerializer",
    "BaseListSerializer",
]
