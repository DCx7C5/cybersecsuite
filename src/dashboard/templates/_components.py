"""Reusable HTML component helpers for the dashboard."""

# ── Shared inline style fragments ─────────────────────────────────────────────
_INPUT_BASE = (
    "width:100%;padding:7px 10px;"
    "background:var(--surface-2);border:1px solid var(--border);"
    "border-radius:var(--radius);color:var(--text-primary);font-size:13px"
)
_LABEL_STYLE = (
    "font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;"
    "color:var(--text-muted);display:block;margin-bottom:4px;font-family:var(--font-mono)"
)


# ── Form helpers ───────────────────────────────────────────────────────────────

def form_label(text: str, *, hint: str = "") -> str:
    """Styled mono uppercase label with optional faint hint."""
    hint_html = (
        f' <span style="color:var(--text-faint);text-transform:none;font-weight:400">{hint}</span>'
        if hint else ""
    )
    return f'<label style="{_LABEL_STYLE}">{text}{hint_html}</label>'


def form_input(
    elem_id: str,
    *,
    placeholder: str = "",
    value: str = "",
    type: str = "text",
    extra_style: str = "",
) -> str:
    """Styled text / number input."""
    style = _INPUT_BASE + (f";{extra_style}" if extra_style else "")
    val = f' value="{value}"' if value else ""
    return (
        f'<input id="{elem_id}" type="{type}"{val} placeholder="{placeholder}" '
        f'style="{style}">'
    )


def form_select(
    elem_id: str,
    options: list[tuple[str, str]],
    *,
    onchange: str = "",
    extra_style: str = "",
) -> str:
    """Styled <select> with (value, label) pairs."""
    style = _INPUT_BASE + (f";{extra_style}" if extra_style else "")
    onchange_attr = f' onchange="{onchange}"' if onchange else ""
    opts = "".join(f'<option value="{v}">{l}</option>' for v, l in options)
    return f'<select id="{elem_id}"{onchange_attr} style="{style}">{opts}</select>'


def form_textarea(
    elem_id: str,
    *,
    rows: int = 4,
    placeholder: str = "",
    mono: bool = False,
    extra_style: str = "",
) -> str:
    """Styled <textarea>."""
    mono_style = ";font-family:var(--font-mono)" if mono else ""
    style = _INPUT_BASE + ";resize:vertical" + mono_style + (f";{extra_style}" if extra_style else "")
    return (
        f'<textarea id="{elem_id}" rows="{rows}" placeholder="{placeholder}" '
        f'style="{style}"></textarea>'
    )


def form_field(label: str, *widgets: str, hint: str = "") -> str:
    """Stacked label + one or more widgets in a single <div>."""
    inner = "\n  ".join(w for w in widgets if w)
    return f'<div>\n  {form_label(label, hint=hint)}\n  {inner}\n</div>'


# ── Buttons & action bars ──────────────────────────────────────────────────────

def btn(label: str, *, onclick: str = "", cls: str = "btn", extra_style: str = "") -> str:
    """Generic button."""
    onclick_attr = f' onclick="{onclick}"' if onclick else ""
    style_attr = f' style="{extra_style}"' if extra_style else ""
    return f'<button class="{cls}"{onclick_attr}{style_attr}>{label}</button>'


def status_span(elem_id: str, *, cls: str = "") -> str:
    """Small status / feedback span wired to a JS element ID."""
    style = "font-size:11px;font-family:var(--font-mono);color:var(--text-muted)"
    cls_attr = f' class="{cls}"' if cls else ""
    return f'<span id="{elem_id}"{cls_attr} style="{style}"></span>'


def action_bar(*items: str, gap: int = 3) -> str:
    """Horizontal flex row for buttons + status spans."""
    inner = "\n  ".join(i for i in items if i)
    return f'<div style="display:flex;align-items:center;gap:{gap * 4}px">\n  {inner}\n</div>'


def panel_toolbar(title: str, *actions: str) -> str:
    """Panel header: title left, action buttons right."""
    acts = "\n    ".join(a for a in actions if a)
    return (
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">\n'
        f'  <h3 class="text-lg font-semibold">{title}</h3>\n'
        f'  <div style="display:flex;align-items:center;gap:8px">\n    {acts}\n  </div>\n'
        '</div>'
    )


# ── Filter / search bar ────────────────────────────────────────────────────────

def filter_bar(
    input_id: str,
    placeholder: str,
    oninput: str,
    count_id: str = "",
    *extra_widgets: str,
) -> str:
    """Compact search input with optional count badge and extra widgets."""
    count = (
        f'<span id="{count_id}" style="font-size:12px;color:var(--text-muted);font-family:var(--font-mono)"></span>'
        if count_id else ""
    )
    extras = "\n  ".join(e for e in extra_widgets if e)
    return (
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">\n'
        f'  <input id="{input_id}" type="text" placeholder="{placeholder}" oninput="{oninput}"\n'
        f'    style="flex:1;max-width:260px;padding:6px 10px;background:var(--surface-2);'
        f'border:1px solid var(--border);border-radius:var(--radius);'
        f'color:var(--text-primary);font-size:13px">\n'
        f'  {count}\n'
        f'  {extras}\n'
        f'</div>'
    )


# ── Rich display components ────────────────────────────────────────────────────

def code_preview(elem_id: str, *, hidden: bool = True, max_h: str = "300px") -> str:
    """Scrollable <pre> block for generated code / JSON preview."""
    display = "none" if hidden else "block"
    return (
        f'<pre id="{elem_id}" style="display:{display};margin-top:16px;padding:14px;'
        f'background:var(--bg-deep);border:1px solid var(--border);'
        f'border-radius:var(--radius);font-size:11px;font-family:var(--font-mono);'
        f'color:var(--text-primary);white-space:pre-wrap;'
        f'max-height:{max_h};overflow-y:auto"></pre>'
    )


def modal_overlay(elem_id: str, *content: str, width: str = "600px") -> str:
    """Full-screen dark overlay with a centred content card."""
    inner = "\n    ".join(c for c in content if c)
    return (
        f'<div id="{elem_id}" style="display:none;position:fixed;inset:0;'
        f'background:rgba(0,0,0,.7);z-index:1000;align-items:center;justify-content:center">\n'
        f'  <div style="background:var(--surface-1);border:1px solid var(--border);'
        f'border-radius:10px;padding:24px;width:{width};max-width:95vw;'
        f'max-height:90vh;overflow-y:auto">\n'
        f'    {inner}\n'
        f'  </div>\n'
        f'</div>'
    )


def section_badge(label: str, color: str) -> str:
    """Coloured pill badge — used for scope indicators, status tags, etc."""
    return (
        f'<span style="display:inline-flex;align-items:center;gap:4px;'
        f'font-size:10px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;'
        f'padding:2px 8px;border-radius:4px;'
        f'background:{color}1a;color:{color};border:1px solid {color}33">'
        f'{label}</span>'
    )


def info_box(text: str, *, color: str = "var(--text-muted)") -> str:
    """Small descriptive paragraph in muted mono text."""
    return (
        f'<p style="font-size:12px;color:{color};margin-bottom:12px;'
        f'font-family:var(--font-mono)">{text}</p>'
    )


def loading_slot(elem_id: str, text: str = "Loading…") -> str:
    """Named div pre-populated with a loading placeholder."""
    return f'<div id="{elem_id}" class="toggles-loading">{text}</div>'


def divider(*, label: str = "", margin: str = "20px 0 16px") -> str:
    """Horizontal rule, optionally with a centred label."""
    if label:
        return (
            f'<div style="display:flex;align-items:center;gap:10px;margin:{margin}">'
            f'<hr style="flex:1;border:none;border-top:1px solid var(--border)">'
            f'<span style="font-size:10px;font-family:var(--font-mono);color:var(--text-faint);white-space:nowrap">{label}</span>'
            f'<hr style="flex:1;border:none;border-top:1px solid var(--border)">'
            f'</div>'
        )
    return f'<hr style="border:none;border-top:1px solid var(--border);margin:{margin}">'


def grid(*cells: str, cols: int = 2, gap: int = 3) -> str:
    """Generic CSS grid wrapper."""
    inner = "\n".join(c for c in cells if c)
    return (
        f'<div style="display:grid;grid-template-columns:repeat({cols},1fr);'
        f'gap:{gap * 4}px;margin-bottom:{gap * 4}px">\n{inner}\n</div>'
    )


def stat_card(elem_id: str, label: str) -> str:
    """Styled stat card (used in forensic tabs — Findings, IOCs, etc.)."""
    return (
        f'<div class="stat-card">'
        f'<div class="stat-value" id="{elem_id}">—</div>'
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
    return f'<h3 class="section-h3">{text}</h3>'


def section_h4(text: str) -> str:
    return f'<h4 class="section-h4">{text}</h4>'


def table_slot(elem_id: str, *, loading: bool = False, loading_text: str = "Loading...") -> str:
    """Placeholder div for renderTable() injection."""
    if loading:
        return f'<div id="{elem_id}" class="loading text-gray-500">{loading_text}</div>'
    return f'<div id="{elem_id}"></div>'


def tab_panel(name: str, title: str, *body: str, hidden: bool = True) -> str:
    """Wraps content in a named tab panel div with accent-bar header."""
    display = ' style="display:none"' if hidden else ""
    content = "\n  ".join(b for b in body if b)
    header = (
        f'<div class="panel-header">'
        f'<div class="panel-accent-bar"></div>'
        f'<div class="panel-title">{title}</div>'
        f'</div>\n  '
        if title else ""
    )
    return (
        f'<div id="tab-{name}" class="card panel-enter"{display}>\n'
        f'  {header}'
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
