"""CSSModule protocol for entry point-based plugin discovery."""

from typing import Protocol, runtime_checkable
from fastapi import APIRouter
from tortoise.models import Model


@runtime_checkable
class CSSModule(Protocol):
    """Protocol for loadable CSS modules via entry_points discovery.

    All modules in css.modules must implement this interface to be
    discoverable by core/loader.py entry_points mechanism.

    Example implementation::

        class MyModule:
            name = "my_module"
            router = APIRouter(prefix="/api/my")
            root_router = APIRouter()
            tortoise_models = [MyModel]
    """

    @property
    def name(self) -> str:
        """Module name for logging and entry_point lookup."""
        ...

    @property
    def router(self) -> APIRouter | None:
        """Optional API router (included in main FastAPI app)."""
        ...

    @property
    def root_router(self) -> APIRouter | None:
        """Optional root-level router (no prefix)."""
        ...

    @property
    def tortoise_models(self) -> list[type[Model]] | None:
        """Optional list of Tortoise ORM models to register."""
        ...

