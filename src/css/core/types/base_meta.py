from abc import ABCMeta
import asyncio
from threading import RLock
from collections.abc import Callable
from typing import Generic, TypeVar, cast, overload, override

T = TypeVar("T")


class SingletonMetaClass(type):
    """Singleton metaclass for sync class instantiation."""

    _instances: dict[type, object] = {}

    @override
    def __call__(cls, *args: object, **kwargs: object) -> object:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AsyncSafeSingletonMeta(ABCMeta):
    """ABC-compatible singleton metaclass."""

    _instances: dict[type, object] = {}
    _lock = RLock()

    @override
    def __call__(cls, *args: object, **kwargs: object) -> object:
        if cls in cls._instances:
            return cls._instances[cls]
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonDecorator(Generic[T]):
    """Decorator object used by ``@singleton``."""

    def __init__(self, target: type[T]):
        self._target = target
        self._instance: T | None = None
        self._lock = RLock()
        self._async_lock = asyncio.Lock()

    def __call__(self, *args: object, **kwargs: object) -> T:
        if self._instance is not None:
            return self._instance
        with self._lock:
            if self._instance is None:
                self._instance = self._target(*args, **kwargs)
        return self._instance

    async def get_instance(self, *args: object, **kwargs: object) -> T:
        if self._instance is not None:
            return self._instance
        async with self._async_lock:
            if self._instance is None:
                self._instance = self._target(*args, **kwargs)
        return self._instance


@overload
def singleton(target: type[T], /) -> type[T]: ...


@overload
def singleton(*, auto_instantiate: bool = False) -> Callable[[type[T]], type[T]]: ...


def singleton(
    target: type[T] | None = None,
    /,
    *,
    auto_instantiate: bool = False,
) -> type[T] | Callable[[type[T]], type[T]]:
    """Use as ``@singleton`` or ``@singleton(auto_instantiate=True)``."""

    def _decorate(cls: type[T]) -> type[T]:
        # Protocols are typing-only contracts and must remain class-like so they
        # can be inherited (e.g., BaseRegistry[T]).
        if bool(getattr(cls, "_is_protocol", False)):
            return cls

        wrapped = SingletonDecorator(cls)
        if auto_instantiate:
            wrapped()
        return cast(type[T], wrapped)

    if target is None:
        return _decorate
    return _decorate(target)
