"""Compatibility bridge for hook runtime surfaces.

Canonical ownership lives in ``css.modules.hooks``.
"""

from css.modules.hooks import (
    BaseHookClass,
    HookBlockedError,
    HookContext,
    HookRegistry,
    InterceptorRegistry,
    hook_registry,
    interceptor_registry,
    on_event,
    post_hook,
    pre_hook,
)

