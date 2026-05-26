"""FastAPI-compatible msgspec Struct base class.

Implements ``__get_pydantic_core_schema__`` so that FastAPI's internal
Pydantic machinery can validate and serialize msgspec Struct subclasses
without requiring Pydantic BaseModel.

This module is the deliberate interoperability boundary: application request
and response values remain ``msgspec.Struct`` instances, while FastAPI still
requires a Pydantic-core schema hook for response-model/OpenAPI generation.
"""

from typing import Any

import msgspec
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class EndpointModel(msgspec.Struct, kw_only=True, frozen=True):
    """Base class for FastAPI endpoint request/response models.

    Subclass this instead of plain ``msgspec.Struct`` in any module that
    uses the struct as a ``response_model``, request body parameter, or
    any other FastAPI-annotated endpoint signature.

    ``kw_only=True`` lifts the msgspec field-ordering constraint so that
    optional (defaulted) fields may appear before required fields.
    ``frozen=True`` prevents accidental mutation.

    Example::

        class MyRequest(EndpointModel):
            name: str
            value: int

        class MyResponse(EndpointModel):
            id: int
            name: str
            created_at: datetime
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                when_used="json",
            ),
        )

    @classmethod
    def _validate(cls, data: Any) -> Any:
        if isinstance(data, cls):
            return data
        if isinstance(data, dict):
            return cls(**data)
        raise TypeError(
            f"Expected dict or {cls.__name__}, got {type(data).__name__}"
        )

    @classmethod
    def _serialize(cls, instance: Any) -> Any:
        return msgspec.to_builtins(instance)
