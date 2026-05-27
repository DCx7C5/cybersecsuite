"""DB model serializer — ORM model ↔ dict bridge.

``DBModelSerializer`` serializes Tortoise ORM model instances to dicts
and back, using ``BaseSerializer`` (not ``BaseModelSerializer``) as its
base. This keeps the ``css.core.serializers`` package clean of ORM
coupling; model-specific serializers in ``css.core.db.models`` use
``BaseModelSerializer`` directly.
"""

from typing import Any, override

from css.core.types.base_serializer import BaseSerializer


class DBModelSerializer(BaseSerializer):
    """Serialize ORM model instances to/from dicts.

    Converts between ``dict[str, Any]`` representations and serialized
    strings. The public API matches ``BaseSerializer`` exactly.

    Attributes:
        _data: Internal dict storage of the serialized model.
    """

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self._data = data or {}

    @classmethod
    @override
    def from_string(cls, data: str) -> DBModelSerializer:
        raise NotImplementedError(
            "DBModelSerializer does not yet support string deserialization"
        )

    @classmethod
    def from_model(cls, model: object) -> DBModelSerializer:
        """Construct a serializer from an ORM model instance.

        Subclasses must override this method.
        """
        raise NotImplementedError

    @override
    def to_string(self) -> str:
        raise NotImplementedError(
            "DBModelSerializer does not yet support string serialization"
        )

    def to_model(self) -> object:
        """Convert the serializer back to an ORM model instance.

        Subclasses must override this method.
        """
        raise NotImplementedError

    @property
    def data(self) -> dict[str, Any]:
        """The underlying dict representation."""
        return self._data

