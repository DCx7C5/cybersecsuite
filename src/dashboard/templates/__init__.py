"""Dashboard HTML template package.

Entry point: build_dashboard_html() → full SPA HTML string.
"""
from ._base import head, header, context_bar, _TOAST_JS
from .panels import all_panels
from ._tabs import tab_bar
from ._bootstrap_modal import bootstrap_modal_html


def build_dashboard_html() -> str:
    sidebar_logo = (
        '<div id="sidebar-logo">\n'
        '  <div class="logo-text">&#x25c6; CyberSecSuite</div>\n'
        '  <div class="logo-sub">COMMAND CONSOLE v2</div>\n'
        '  <button id="sidebar-collapse-btn" class="sidebar-collapse-btn" onclick="toggleSidebar()" title="Collapse sidebar" aria-label="Collapse sidebar" aria-controls="sidebar" aria-expanded="true">&#x25c4;</button>\n'
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
        '<div id="main-content">\n'
        + header()
        + context_bar()
        + '<div id="content">\n'
        + all_panels()
        + '</div>\n'
        + '</div>\n'
    )

    return (
        '<!DOCTYPE html>\n<html lang="en">\n'
        + head()
        + '<body>\n'
        + bootstrap_modal_html()
        + '<div id="shell">\n'
        + sidebar
        + main
        + '</div>\n'
        + _TOAST_JS
        + '\n<script type="module" src="/static/js/index.js"></script>\n</body>\n</html>\n'
    )
