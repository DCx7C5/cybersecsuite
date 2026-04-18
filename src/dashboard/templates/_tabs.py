"""Tab bar: one entry per dashboard tab."""


def tab_bar() -> str:
    tabs = [
        ("providers", "Providers", True),
        ("usage", "Usage &amp; Cost", False),
        ("agents", "&#x1f916; Agents", False),
        ("routing", "&#x1f500; Routing", False),
        ("factory", "&#x1f3ed; Factory", False),
        ("prompts", "&#x1f4dd; Prompts", False),
        ("health", "Health", False),
        ("crypto", "&#x1f512; Crypto", False),
        ("a2a", "&#x1f310; A2A", False),
        ("investigations", "&#x1f50d; Investigations", False),
        ("dbcounts", "&#x1f4ca; DB Counts", False),
        ("cases", "&#x1f4c2; Cases", False),
        ("tasks", "&#x23f1; Tasks", False),
        ("pocs", "&#x1f4a3; PoCs", False),
        ("findings", "&#x1f6a8; Findings", False),
        ("iocs", "&#x1f4cc; IOCs", False),
        ("yara", "&#x1f9ec; YARA", False),
        ("network", "&#x1f5a7; Network", False),
        ("intel", "&#x1f9e0; Intel", False),
        ("audit", "&#x1f4cb; Audit", False),
        ("compliance", "&#x2705; Compliance", False),
        ("agent-query", "&#x1f916; Agent Query", False),
        ("settings", "&#x2699;&#xfe0f; Settings", False),
        ("team-builder", "&#x1f3d7; Team Builder", False),
        ("telemetry", "&#x1f4ca; Telemetry", False),
        ("explorer", "&#x1f50e; Explorer", False),
    ]
    items = []
    for name, label, active in tabs:
        cls = "tab active" if active else "tab"
        items.append(f'    <div class="{cls}" onclick="showTab(\'{name}\')">{label}</div>')
    inner = "\n".join(items)
    return (
        "  <!-- Tabs -->\n"
        '  <div class="flex gap-1 mb-4 border-b border-gray-800 flex-wrap">\n'
        + inner
        + "\n  </div>\n"
    )
