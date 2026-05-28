"""FastAPI-compatible msgspec Struct base class.

Implements ``__get_pydantic_core_schema__`` so that FastAPI's internal
Pydantic machinery can validate and serialize msgspec Struct subclasses
without requiring Pydantic BaseModel.

This module is the deliberate interoperability boundary: application request
and response values remain ``msgspec.Struct`` instances, while FastAPI still
requires a Pydantic-core schema hook for response-model/OpenAPI generation.

The ``_GetCoreSchemaHandler`` Protocol matches the interface FastAPI passes
when calling ``__get_pydantic_core_schema__`` on custom types, without
importing ``pydantic`` directly.
"""

from typing import Protocol

import msgspec


class _GetCoreSchemaHandler(Protocol):
    """Protocol matching pydantic's GetCoreSchemaHandler interface.

    Implemented as an inline Protocol so that FastAPI can call
    ``__get_pydantic_core_schema__`` without requiring a module-level
    import of ``pydantic`` or ``pydantic_core``.
    """

    def __call__(self, source_type: type, /) -> dict[str, object]:
        """Call the inner handler and get the CoreSchema it returns.

        This will call the next CoreSchema modifying function up until it calls
        into Pydantic's internal schema generation machinery, which will raise a
        ``pydantic.errors.PydanticSchemaGenerationError`` if it cannot generate
        a CoreSchema for the given source type.

        Args:
            source_type: The input type.

        Returns:
            The ``pydantic-core`` CoreSchema generated.
        """
        ...

    def generate_schema(self, source_type: type, /) -> dict[str, object]:
        """Generate a schema unrelated to the current context.

        Use this function if e.g. you are handling schema generation for a
        sequence and want to generate a schema for its items. Otherwise you
        may end up applying a ``min_length`` constraint intended for the
        sequence itself to its items.

        Args:
            source_type: The input type.

        Returns:
            The ``pydantic-core`` CoreSchema generated.
        """
        ...

    def resolve_ref_schema(
        self, maybe_ref_schema: dict[str, object], /
    ) -> dict[str, object]:
        """Resolve a ``definition-ref`` schema to its concrete schema.

        If *maybe_ref_schema* is not a ``definition-ref`` schema it is
        returned as-is.

        Args:
            maybe_ref_schema: A ``CoreSchema``, ref-based or not.

        Raises:
            LookupError: If the ``ref`` key is not found.

        Returns:
            The concrete ``CoreSchema``.
        """
        ...

    @property
    def field_name(self) -> str | None:
        """The name of the closest field to this validator, or ``None``."""
        ...

    def _get_types_namespace(self) -> tuple[dict[str, object], ...]:
        """Internal method used during type resolution for serializer annotations.

        Returns:
            A tuple with (types_namespace, parent_namespace).
            This is considered an implementation detail of pydantic.
        """
        ...


class BaseEndpoint(msgspec.Struct, kw_only=True, frozen=True):
    """Base class for FastAPI endpoint request/response models.

    Subclass this instead of plain ``msgspec.Struct`` in any module that
    uses the struct as a ``response_model``, request body parameter, or
    any other FastAPI-annotated endpoint signature.

    ``kw_only=True`` lifts the msgspec field-ordering constraint so that
    optional (defaulted) fields may appear before required fields.
    ``frozen=True`` prevents accidental mutation.

    Example::

        class MyRequest(BaseEndpoint):
            name: str
            value: int

        class MyResponse(BaseEndpoint):
            id: int
            name: str
            created_at: datetime
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type, handler_info: _GetCoreSchemaHandler
    ):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                when_used="json",
            ),
        )

    @classmethod
    def _validate(cls, data: object) -> object:
        if isinstance(data, cls):
            return data
        try:
            return msgspec.json.decode(
                data if isinstance(data, bytes) else msgspec.json.encode(data),
                type=cls
            )
        except Exception as e:
            raise TypeError(
                f"Validation failed for {cls.__name__}: {e}"
            ) from e

    @classmethod
    def _serialize(cls, instance: object) -> object:
        return msgspec.to_builtins(instance)
