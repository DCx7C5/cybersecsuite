"""Jinja2 environment for the dashboard component library.

Usage from Python panels / tests:
    from dashboard.templates.jinja_env import get_env, render_macro

    env = get_env()
    html = render_macro('components/base.html', 'card',
                        title='Health', icon='❤', subtitle='Live')
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, ChoiceLoader, select_autoescape

_TEMPLATES_DIR = Path(__file__).parent  # src/dashboard/templates/


@lru_cache(maxsize=1)
def get_env() -> Environment:
    """Return a cached Jinja2 Environment scoped to the dashboard template tree."""
    loader = FileSystemLoader(str(_TEMPLATES_DIR), followlinks=True)
    env = Environment(
        loader=loader,
        autoescape=select_autoescape(["html"]),
        keep_trailing_newline=True,
        # Allow macro caller() blocks
        extensions=[],
    )
    return env


def render_macro(
    template_path: str,
    macro_name: str,
    **kwargs: object,
) -> str:
    """Render a single Jinja2 macro from a component template.

    Example:
        render_macro('components/base.html', 'badge', text='OK', variant='ok')
    """
    env = get_env()
    # Build a tiny wrapper template that imports and calls the macro
    wrapper = (
        "{{% from '{tpl}' import {macro} %}}"
        "{{{{ {macro}({args}) }}}}"
    ).format(
        tpl=template_path,
        macro=macro_name,
        args=", ".join(f"{k}={v!r}" for k, v in kwargs.items()),
    )
    tpl = env.from_string(wrapper)
    return tpl.render()


def render_block(template_path: str, ctx: dict | None = None) -> str:
    """Render a full component template file with a given context dict."""
    env = get_env()
    tpl = env.get_template(template_path)
    return tpl.render(**(ctx or {}))
