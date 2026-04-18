"""Reusable HTML component helpers for the dashboard."""


def stat_card(elem_id: str, label: str) -> str:
    """Styled stat card (used in forensic tabs — Findings, IOCs, etc.)."""
    return (
        f'<div class="stat-card">'
        f'<div class="stat-value" id="{elem_id}">\u2014</div>'
        f'<div class="stat-label">{label}</div>'
        f'</div>'
    )


def stat_grid(*cards: str, cols: int = 4) -> str:
    """Responsive grid of stat_card() items."""
    inner = "".join(cards)
    return f'<div class="grid grid-cols-2 md:grid-cols-{cols} gap-3 mb-4">{inner}</div>'


def mini_card(elem_id: str, label: str, color: str = "") -> str:
    """Compact .card counter (used in Cases, Tasks, Crypto, etc.)."""
    val_cls = f"text-2xl font-bold{' ' + color if color else ''}"
    return (
        f'<div class="card text-center">'
        f'<div class="{val_cls}" id="{elem_id}">-</div>'
        f'<div class="text-xs text-gray-500">{label}</div>'
        f'</div>'
    )


def mini_grid(*cards: str, cols: int = 3) -> str:
    """Grid of mini_card() items."""
    inner = "".join(cards)
    return f'<div class="grid grid-cols-{cols} gap-4 mb-4">{inner}</div>'


def section_h3(text: str) -> str:
    return f'<h3 class="text-lg font-semibold mb-3">{text}</h3>'


def section_h4(text: str) -> str:
    return f'<h4 class="text-sm font-semibold text-gray-400 mb-2 mt-4">{text}</h4>'


def table_slot(elem_id: str, *, loading: bool = False, loading_text: str = "Loading...") -> str:
    """Placeholder div for renderTable() injection."""
    if loading:
        return f'<div id="{elem_id}" class="loading text-gray-500">{loading_text}</div>'
    return f'<div id="{elem_id}"></div>'


def tab_panel(name: str, title: str, *body: str, hidden: bool = True) -> str:
    """Wraps content in a named tab panel div."""
    display = ' style="display:none"' if hidden else ""
    content = "\n  ".join(b for b in body if b)
    h3 = section_h3(title) if title else ""
    return (
        f'<div id="tab-{name}" class="card"{display}>\n'
        f'  {h3}\n'
        f'  {content}\n'
        f'</div>\n'
    )


def simple_panel(name: str, title: str, content_id: str, loading_text: str) -> str:
    """Tab panel with a single JS-rendered content slot."""
    return tab_panel(
        name,
        title,
        table_slot(content_id, loading=True, loading_text=loading_text),
    )
