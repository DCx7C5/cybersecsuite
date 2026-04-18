"""Dashboard HTML template package.

Entry point: build_dashboard_html() → full SPA HTML string.
"""
from ._base import head, header, stats_row, tiers_row
from ._js import _JS
from ._panels import all_panels
from ._tabs import tab_bar


def build_dashboard_html() -> str:
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n"
        + head()
        + "<body class=\"min-h-screen\">\n"
        + "<div class=\"max-w-7xl mx-auto px-4 py-6\">\n"
        + header()
        + stats_row()
        + tiers_row()
        + tab_bar()
        + all_panels()
        + "</div>\n\n<script>\n"
        + _JS
        + "</script>\n</body>\n</html>\n"
    )
