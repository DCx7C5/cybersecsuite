"""Local pydantic compatibility stubs — avoids importing pydantic.

``GetCoreSchemaHandler`` is copied from pydantic source
(pydantic/_internal/_schema_generation_shared.py) so that the
``BaseEndpoint.__get_pydantic_core_schema__`` hook works without
requiring ``pydantic`` as a direct dependency.

``CoreSchema`` is re-exported as ``Any`` — it is a large Union
type alias from ``pydantic_core`` that provides no runtime value.

Original ``GetCoreSchemaHandler`` source (pydantic v2):

class GetCoreSchemaHandler:
    def __call__(self, source_type: Any, /) -> core_schema.CoreSchema: ...
    def generate_schema(self, source_type: Any, /) -> core_schema.CoreSchema: ...
    def resolve_ref_schema(
        self, maybe_ref_schema: core_schema.CoreSchema, /
    ) -> core_schema.CoreSchema: ...
    @property
    def field_name(self) -> str | None: ...
    def _get_types_namespace(self) -> NamespacesTuple: ...
"""

from typing import Any, Protocol


CoreSchema = Any


class GetCoreSchemaHandler(Protocol):
    """Handler to call into the next CoreSchema schema generation function.

    This is a local Protocol matching pydantic's ``GetCoreSchemaHandler``
    interface.  FastAPI uses it internally when calling
    ``__get_pydantic_core_schema__`` on custom types.
    """

    def __call__(self, source_type: type[Any], /) -> CoreSchema: ...

    def generate_schema(self, source_type: type[Any], /) -> CoreSchema: ...

    def resolve_ref_schema(self, maybe_ref_schema: CoreSchema, /) -> CoreSchema: ...

    @property
    def field_name(self) -> str | None: ...

    def _get_types_namespace(self) -> Any: ...
