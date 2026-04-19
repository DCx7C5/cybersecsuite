"""Dashboard HTML template package.

Entry point: build_dashboard_html() → full SPA HTML string.
"""
from ._base import head, header, stats_row, tiers_row
from ._js import _JS
from ._panels import all_panels
from ._tabs import tab_bar, first_tab


def build_dashboard_html() -> str:
    sidebar_logo = (
        '<div id="sidebar-logo">\n'
        '  <div class="logo-text">&#x25c6; CyberSecSuite</div>\n'
        '  <div class="logo-sub">COMMAND CONSOLE v2</div>\n'
        '</div>\n'
        '<div id="sidebar-status">'
        '<span class="status-dot"></span>SYSTEM ONLINE'
        '</div>\n'
    )

    sidebar = (
        '<aside id="sidebar">\n'
        + sidebar_logo
        + tab_bar()
        + '</aside>\n'
    )

    main = (
        '<div id="main">\n'
        + header()
        + '<div id="content">\n'
        + stats_row()
        + tiers_row()
        + all_panels()
        + '</div>\n'
        + '</div>\n'
    )

    return (
        '<!DOCTYPE html>\n<html lang="en">\n'
        + head()
        + '<body>\n'
        + '<div id="shell">\n'
        + sidebar
        + main
        + '</div>\n\n<script>\n'
        + _JS
        + '</script>\n</body>\n</html>\n'
    )
