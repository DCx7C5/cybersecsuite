"""Synchronous/mutating interceptor chain for runtime event lifecycles."""

import asyncio
import fnmatch
import inspect
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import TypeAlias

import msgspec

from css.core.logger import getLogger
from css.core.types.base_enums import HookErrorStrategy
from css.core.types.base_meta import singleton

logger = getLogger(__name__)

HookValue: TypeAlias = object
HookPayload: TypeAlias = dict[str, HookValue]
InterceptorHandler: TypeAlias = Callable[
    ["HookContext"],
    "HookContext | None | Awaitable[HookContext | None]",
]


class HookBlockedError(RuntimeError):
    """Raised by interceptors to block execution."""

    def __init__(self, message: str, *, namespace: str | None = None):
        super().__init__(message)
        self.namespace = namespace


class HookContext(msgspec.Struct, kw_only=True):
    """Mutable context that flows through pre- / post-interceptor chains."""

    namespace: str
    input: HookPayload = msgspec.field(default_factory=dict)
    output: HookValue | None = None
    error: str | None = None
    correlation_id: str = msgspec.field(default_factory=lambda: str(uuid.uuid4()))
    metadata: HookPayload = msgspec.field(default_factory=dict)
    started_at: float = msgspec.field(default_factory=time.monotonic)
    duration_ms: float | None = None
    error_strategy: HookErrorStrategy = HookErrorStrategy.PRESERVE_EXISTING

    def block(self, message: str) -> None:
        """Block execution from inside an interceptor."""
        raise HookBlockedError(message, namespace=self.namespace)

    def set_args(self, args: tuple[object, ...]) -> None:
        """Replace positional args for downstream execution."""
        self.input["args"] = list(args)

    def set_kwargs(self, kwargs: dict[str, object]) -> None:
        """Replace keyword args for downstream execution."""
        self.input["kwargs"] = dict(kwargs)

    def get_args(self) -> tuple[object, ...]:
        """Read positional args for execution."""
        value = self.input.get("args", [])
        if isinstance(value, list):
            return tuple(value)
        return ()

    def get_kwargs(self) -> dict[str, object]:
        """Read keyword args for execution."""
        value = self.input.get("kwargs", {})
        if isinstance(value, dict):
            return dict(value)
        return {}


class _InterceptorBinding:
    """Runtime binding for one interceptor handler."""

    def __init__(
        self,
        pattern: str,
        handler: InterceptorHandler,
        priority: int,
        stage: str,
    ) -> None:
        self.pattern = pattern
        self.handler = handler
        self.priority = priority
        self.stage = stage

    def matches(self, namespace: str) -> bool:
        return fnmatch.fnmatch(namespace, self.pattern)


@singleton(auto_instantiate=True)
class InterceptorRegistry:
    """Registry for pre- / post-interceptors with glob matching and priorities."""

    _initialized: bool = False

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._pre_bindings: list[_InterceptorBinding] = []
        self._post_bindings: list[_InterceptorBinding] = []
        self._timeout_seconds = 10.0

    def pre(
        self,
        pattern: str,
        *,
        priority: int = 50,
    ) -> Callable[[InterceptorHandler], InterceptorHandler]:
        """Decorator to register a pre-interceptor."""

        def decorator(handler: InterceptorHandler) -> InterceptorHandler:
            self._pre_bindings.append(
                _InterceptorBinding(
                    pattern=pattern,
                    handler=handler,
                    priority=priority,
                    stage="pre",
                )
            )
            return handler

        return decorator

    def post(
        self,
        pattern: str,
        *,
        priority: int = 50,
    ) -> Callable[[InterceptorHandler], InterceptorHandler]:
        """Decorator to register a post-interceptor."""

        def decorator(handler: InterceptorHandler) -> InterceptorHandler:
            self._post_bindings.append(
                _InterceptorBinding(
                    pattern=pattern,
                    handler=handler,
                    priority=priority,
                    stage="post",
                )
            )
            return handler

        return decorator

    def list_pre_patterns(self) -> list[str]:
        return sorted({item.pattern for item in self._pre_bindings})

    def list_post_patterns(self) -> list[str]:
        return sorted({item.pattern for item in self._post_bindings})

    async def run_pre(self, context: HookContext) -> HookContext:
        """Execute matching pre-interceptors synchronously in priority order."""
        return await self._run_chain(context, stage="pre")

    async def run_post(self, context: HookContext) -> HookContext:
        """Execute matching post-interceptors synchronously in priority order."""
        return await self._run_chain(context, stage="post")

    async def _run_chain(self, context: HookContext, *, stage: str) -> HookContext:
        bindings = self._matching_bindings(context.namespace, stage=stage)
        current_context = context
        for binding in bindings:
            current_context = await self._call_interceptor(binding, current_context)
        return current_context

    def _matching_bindings(self, namespace: str, *, stage: str) -> list[_InterceptorBinding]:
        source = self._pre_bindings if stage == "pre" else self._post_bindings
        matches = [binding for binding in source if binding.matches(namespace)]
        matches.sort(key=lambda item: item.priority)
        return matches

    async def _call_interceptor(
        self,
        binding: _InterceptorBinding,
        context: HookContext,
    ) -> HookContext:
        try:
            result = await asyncio.wait_for(
                self._invoke(binding.handler, context),
                timeout=self._timeout_seconds,
            )
        except HookBlockedError:
            raise
        except BaseException as error:
            message = (
                f"interceptor failed "
                f"(stage={binding.stage}, pattern={binding.pattern}): {error}"
            )
            if context.error_strategy == HookErrorStrategy.PRESERVE_EXISTING:
                logger.warning(message)
                return context
            if context.error_strategy == HookErrorStrategy.WARN:
                logger.warning(message)
                return context
            if context.error_strategy == HookErrorStrategy.LOG:
                logger.info(message)
                return context
            raise

        if result is None:
            return context
        return result

    @staticmethod
    async def _invoke(handler: InterceptorHandler, context: HookContext) -> HookContext | None:
        if inspect.iscoroutinefunction(handler):
            return await handler(context)
        result = await asyncio.to_thread(handler, context)
        if inspect.isawaitable(result):
            return await result
        return result


def get_interceptor_registry() -> InterceptorRegistry:
    """Return typed singleton InterceptorRegistry instance."""
    return InterceptorRegistry()


class InterceptorRegistryHandle:
    """Typed proxy for InterceptorRegistry singleton methods."""

    def pre(
        self,
        pattern: str,
        *,
        priority: int = 50,
    ) -> Callable[[InterceptorHandler], InterceptorHandler]:
        return get_interceptor_registry().pre(pattern, priority=priority)

    def post(
        self,
        pattern: str,
        *,
        priority: int = 50,
    ) -> Callable[[InterceptorHandler], InterceptorHandler]:
        return get_interceptor_registry().post(pattern, priority=priority)

    async def run_pre(self, context: HookContext) -> HookContext:
        return await get_interceptor_registry().run_pre(context)

    async def run_post(self, context: HookContext) -> HookContext:
        return await get_interceptor_registry().run_post(context)

    def list_pre_patterns(self) -> list[str]:
        return get_interceptor_registry().list_pre_patterns()

    def list_post_patterns(self) -> list[str]:
        return get_interceptor_registry().list_post_patterns()


interceptor_registry = InterceptorRegistryHandle()


def pre_hook(
    pattern: str,
    *,
    priority: int = 50,
) -> Callable[[InterceptorHandler], InterceptorHandler]:
    return get_interceptor_registry().pre(pattern, priority=priority)


def post_hook(
    pattern: str,
    *,
    priority: int = 50,
) -> Callable[[InterceptorHandler], InterceptorHandler]:
    return get_interceptor_registry().post(pattern, priority=priority)


