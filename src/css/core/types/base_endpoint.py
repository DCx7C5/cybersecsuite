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
    """Minimal protocol matching pydantic's GetCoreSchemaHandler interface."""

    def __call__(self, source_type: type, /) -> dict[str, object]: ...

    def generate_schema(self, source_type: type, /) -> dict[str, object]: ...

    def resolve_ref_schema(self, maybe_ref_schema: dict[str, object], /) -> dict[str, object]: ...

    @property
    def field_name(self) -> str | None: ...


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
    ) -> dict[str, object]:
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
