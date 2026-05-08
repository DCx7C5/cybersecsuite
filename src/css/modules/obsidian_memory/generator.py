"""
CanvasGenerator — create Obsidian Canvas files for forensic investigations.

Ported from ~/Projects/claude-canvas/scripts/canvas_template.py and extended
with 6 forensic-specific archetypes. All 12 original archetypes are preserved.

JSON Canvas spec: https://jsoncanvas.org/
Format: {"nodes": [...], "edges": [...]}

Node types: text, file, link, group
Edge fields: id, fromNode, toNode, label, toEnd (arrow|none)
"""


import json
import math
import time
from pathlib import Path
from typing import Any

GRID = 20
H_GAP = 60
V_GAP = 40

# Canonical templates dir — ships with cybersecsuite
_TEMPLATES_DIR = Path(__file__).parent / "templates"

_id_counter = 0


def _snap(value: int | float) -> int:
    return round(value / GRID) * GRID


def _gen_id(prefix: str = "n", slug: str = "") -> str:
    global _id_counter
    _id_counter += 1
    ts = int(time.time())
    if slug:
        slug = slug.lower().replace(" ", "-")[:20]
        return f"{prefix}-{slug}-{ts}-{_id_counter}"
    return f"{prefix}-{ts}-{_id_counter}"


def _reset_counter() -> None:
    global _id_counter
    _id_counter = 0


# ── Layout algorithms (ported from claude-canvas) ─────────────────────────────

def _layout_grid(content: list[dict], columns: int | None = None) -> list[dict]:
    if not content:
        return content
    n = len(content)
    if columns is None:
        columns = max(2, min(6, math.ceil(math.sqrt(n))))
    max_w = max(node["width"] for node in content)
    max_h = max(node["height"] for node in content)
    cell_w = max_w + H_GAP
    cell_h = max_h + V_GAP
    for i, node in enumerate(content):
        col = i % columns
        row = i // columns
        node["x"] = _snap(col * cell_w)
        node["y"] = _snap(row * cell_h)
    return content


def _layout_linear_vertical(nodes: list[dict], start_y: int = 0, gap: int = V_GAP) -> list[dict]:
    y = start_y
    for node in nodes:
        node["x"] = 0
        node["y"] = y
        y += node["height"] + gap
    return nodes


def _layout_linear_horizontal(nodes: list[dict], start_x: int = 0, gap: int = H_GAP) -> list[dict]:
    x = start_x
    for node in nodes:
        node["x"] = x
        node["y"] = 0
        x += node["width"] + gap
    return nodes


def _layout_dagre(content: list[dict], edges: list[dict], direction: str = "TB") -> list[dict]:
    """Simplified hierarchical layout for flowcharts/attack graphs."""
    if not content:
        return content
    node_map = {n["id"]: n for n in content}
    node_ids = set(node_map)
    children: dict[str, list[str]] = {nid: [] for nid in node_ids}
    parents: dict[str, list[str]] = {nid: [] for nid in node_ids}
    for e in edges:
        fn, tn = e.get("fromNode"), e.get("toNode")
        if fn in node_ids and tn in node_ids:
            children[fn].append(tn)
            parents[tn].append(fn)

    # Assign layers via topological sort
    layers: dict[str, int] = {}
    queue = [nid for nid in node_ids if not parents[nid]]
    if not queue:
        queue = list(node_ids)[:1]
    for nid in queue:
        layers[nid] = 0
    changed = True
    iterations = 0
    while changed and iterations < 1000:
        changed = False
        iterations += 1
        for nid in node_ids:
            if nid not in layers:
                p_layers = [layers[p] for p in parents[nid] if p in layers]
                if p_layers:
                    new_layer = max(p_layers) + 1
                    if layers.get(nid, -1) != new_layer:
                        layers[nid] = new_layer
                        changed = True
                else:
                    layers[nid] = 0

    # Group nodes by layer
    layer_groups: dict[int, list[str]] = {}
    for nid, layer in layers.items():
        layer_groups.setdefault(layer, []).append(nid)

    max_w = max(n["width"] for n in content) + H_GAP
    max_h = max(n["height"] for n in content) + V_GAP

    for layer_idx, layer_nodes in sorted(layer_groups.items()):
        for i, nid in enumerate(layer_nodes):
            node = node_map[nid]
            count = len(layer_nodes)
            if direction in ("TB", "BT"):
                offset = -(count - 1) * max_w / 2
                node["x"] = _snap(offset + i * max_w)
                node["y"] = _snap(layer_idx * max_h)
            else:
                offset = -(count - 1) * max_h / 2
                node["x"] = _snap(layer_idx * max_w)
                node["y"] = _snap(offset + i * max_h)

    return content


def _layout_radial(content: list[dict]) -> list[dict]:
    """Center node surrounded by orbiting nodes."""
    if not content:
        return content
    if len(content) == 1:
        content[0]["x"] = 0
        content[0]["y"] = 0
        return content
    center = content[0]
    center["x"] = 0
    center["y"] = 0
    rest = content[1:]
    radius = max(300, len(rest) * 60)
    for i, node in enumerate(rest):
        angle = (2 * math.pi * i) / len(rest) - math.pi / 2
        node["x"] = _snap(radius * math.cos(angle) - node["width"] / 2)
        node["y"] = _snap(radius * math.sin(angle) - node["height"] / 2)
    return content


# ── Template engine (ported from claude-canvas) ───────────────────────────────

def _apply_layout(nodes: list[dict], edges: list[dict], algorithm: str) -> list[dict]:
    groups = [n for n in nodes if n.get("type") == "group"]
    content = [n for n in nodes if n.get("type") != "group"]
    if algorithm == "grid":
        content = _layout_grid(content)
    elif algorithm in ("dagre", "hierarchical"):
        content = _layout_dagre(content, edges)
    elif algorithm == "radial":
        content = _layout_radial(content)
    elif algorithm == "linear-vertical":
        content = _layout_linear_vertical(content)
    elif algorithm == "linear-horizontal":
        content = _layout_linear_horizontal(content)
    return groups + content


def _instantiate(template_name: str, params: dict[str, Any], output_path: Path) -> dict[str, Any]:
    """Load a template JSON, substitute params, write .canvas file."""
    _reset_counter()

    tmpl_path = _TEMPLATES_DIR / f"{template_name}.json"
    if not tmpl_path.exists():
        return {"success": False, "error": f"Template not found: {template_name}"}

    template = json.loads(tmpl_path.read_text(encoding="utf-8"))
    defaults = template.get("defaults", {})
    merged = {**defaults, **params}

    title = str(merged.get("title", template.get("name", template_name)))
    color_title = str(merged.get("color_title", "6"))
    color_body = str(merged.get("color_body", "4"))
    color_accent = str(merged.get("color_accent", "5"))

    nodes: list[dict] = []
    edges: list[dict] = []
    generated_ids: dict[str, list[str]] = {}

    for nt in template.get("node_templates", []):
        role = nt.get("role", "node")
        node_type = nt.get("type", "text")
        repeat = nt.get("repeat", 1)

        if isinstance(repeat, str) and repeat.startswith("$"):
            repeat = int(merged.get(repeat[1:], nt.get("repeat_default", 1)))

        ids_for_role: list[str] = []
        for i in range(int(repeat)):
            nid = _gen_id({"text": "text", "group": "zone", "file": "file", "link": "link"}.get(node_type, "n"), f"{role}-{i}")
            ids_for_role.append(nid)
            node: dict[str, Any] = {
                "id": nid, "type": node_type, "x": 0, "y": 0,
                "width": nt.get("width", 300), "height": nt.get("height", 120),
            }
            color = nt.get("color", "")
            if color:
                color = color.replace("$color_title", color_title).replace("$color_body", color_body).replace("$color_accent", color_accent)
                node["color"] = color

            if node_type == "text":
                text = nt.get("text", f"## {role} {i+1}").replace("$title", title).replace("{n}", str(i + 1))
                node["text"] = text
            elif node_type == "group":
                label = nt.get("label", f"{role} {i+1}").replace("$title", title).replace("{n}", str(i + 1))
                node["label"] = label
            elif node_type == "file":
                node["file"] = nt.get("file", f"file-{i+1}.md")
            elif node_type == "link":
                node["url"] = nt.get("url", "https://example.com")

            nodes.append(node)
        generated_ids[role] = ids_for_role

    for et in template.get("edge_templates", []):
        from_ids = generated_ids.get(et.get("from_role", ""), [])
        to_ids = generated_ids.get(et.get("to_role", ""), [])
        pattern = et.get("pattern", "sequential")
        label = et.get("label", "")
        if pattern == "sequential":
            if et.get("from_role") == et.get("to_role"):
                for i in range(len(from_ids) - 1):
                    edges.append({"id": _gen_id("e"), "fromNode": from_ids[i], "toNode": from_ids[i + 1], "toEnd": "arrow", **({"label": label} if label else {})})
            else:
                for i in range(min(len(from_ids), len(to_ids))):
                    edges.append({"id": _gen_id("e"), "fromNode": from_ids[i], "toNode": to_ids[i], "toEnd": "arrow", **({"label": label} if label else {})})
        elif pattern == "broadcast" and from_ids:
            for tid in to_ids:
                edges.append({"id": _gen_id("e"), "fromNode": from_ids[0], "toNode": tid, "toEnd": "arrow", **({"label": label} if label else {})})

    algo = template.get("layout", "grid")
    nodes = _apply_layout(nodes, edges, algo)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = {"nodes": nodes, "edges": edges}
    output_path.write_text(json.dumps(canvas, indent=2) + "\n", encoding="utf-8")

    return {
        "success": True, "template": template_name, "output": str(output_path),
        "nodes": len(nodes), "edges": len(edges),
    }


# ── Forensic archetypes ────────────────────────────────────────────────────────

def _make_attack_graph(title: str, stages: list[dict[str, str]]) -> dict[str, Any]:
    """
    MITRE ATT&CK kill chain graph.
    stages: [{"name": "Initial Access", "technique": "T1190", "detail": "..."}, ...]
    """
    _reset_counter()
    nodes: list[dict] = []
    edges: list[dict] = []
    colors = ["6", "3", "5", "4", "1", "2", "6", "3"]

    x = 0
    prev_id: str | None = None
    for i, stage in enumerate(stages):
        nid = _gen_id("stage", stage.get("name", f"stage-{i}"))
        text = f"## {stage.get('name', f'Stage {i+1}')}\n\n"
        if stage.get("technique"):
            text += f"**{stage['technique']}**\n\n"
        if stage.get("detail"):
            text += stage["detail"]
        node: dict[str, Any] = {
            "id": nid, "type": "text", "x": x, "y": 0,
            "width": 280, "height": 160,
            "text": text, "color": colors[i % len(colors)],
        }
        nodes.append(node)
        if prev_id:
            edges.append({"id": _gen_id("e"), "fromNode": prev_id, "toNode": nid, "toEnd": "arrow"})
        prev_id = nid
        x += 320

    return {"nodes": nodes, "edges": edges}


def _make_ioc_map(title: str, iocs: list[dict[str, str]]) -> dict[str, Any]:
    """
    IOC relationship map with type-colored zones.
    iocs: [{"type": "ip"|"domain"|"hash"|"email"|"url", "value": "...", "note": "..."}, ...]
    """
    _reset_counter()
    nodes: list[dict] = []
    edges: list[dict] = []

    type_colors = {"ip": "3", "domain": "5", "hash": "4", "email": "1", "url": "6", "file": "2"}
    type_groups: dict[str, list[dict[str, str]]] = {}
    for ioc in iocs:
        t = ioc.get("type", "unknown")
        type_groups.setdefault(t, []).append(ioc)

    # Title card
    title_id = _gen_id("title")
    nodes.append({"id": title_id, "type": "text", "x": 0, "y": -200, "width": 400, "height": 80,
                  "text": f"# {title}", "color": "6"})

    zone_x = 0
    for ioc_type, ioc_list in sorted(type_groups.items()):
        zone_w = 340
        zone_h = len(ioc_list) * 100 + 60
        zone_id = _gen_id("zone", ioc_type)
        nodes.append({"id": zone_id, "type": "group", "x": zone_x, "y": 0,
                      "width": zone_w, "height": zone_h,
                      "label": ioc_type.upper(), "color": type_colors.get(ioc_type, "4")})
        for j, ioc in enumerate(ioc_list):
            nid = _gen_id("ioc", ioc.get("value", f"ioc-{j}"))
            text = f"**{ioc.get('value', '?')}**"
            if ioc.get("note"):
                text += f"\n\n{ioc['note']}"
            nodes.append({"id": nid, "type": "text",
                          "x": zone_x + 20, "y": 50 + j * 100,
                          "width": 300, "height": 80, "text": text,
                          "color": type_colors.get(ioc_type, "4")})
            edges.append({"id": _gen_id("e"), "fromNode": title_id, "toNode": nid, "toEnd": "arrow"})
        zone_x += zone_w + H_GAP

    return {"nodes": nodes, "edges": edges}


def _make_timeline(title: str, events: list[dict[str, str]]) -> dict[str, Any]:
    """
    Incident timeline — horizontal layout.
    events: [{"date": "2024-01-01", "event": "...", "severity": "low|medium|high|critical"}, ...]
    """
    _reset_counter()
    nodes: list[dict] = []
    edges: list[dict] = []
    sev_colors = {"critical": "1", "high": "3", "medium": "5", "low": "4"}

    title_id = _gen_id("title")
    nodes.append({"id": title_id, "type": "text", "x": 0, "y": 0, "width": 400, "height": 60,
                  "text": f"# {title}", "color": "6"})

    x = 0
    prev_id = title_id
    for i, event in enumerate(events):
        nid = _gen_id("event", f"t{i}")
        sev = event.get("severity", "medium")
        text = f"### {event.get('date', f'T+{i}')}\n\n{event.get('event', '')}"
        node: dict[str, Any] = {
            "id": nid, "type": "text", "x": x, "y": 120,
            "width": 280, "height": 140, "text": text,
            "color": sev_colors.get(sev, "4"),
        }
        nodes.append(node)
        edges.append({"id": _gen_id("e"), "fromNode": prev_id, "toNode": nid, "toEnd": "arrow"})
        prev_id = nid
        x += 320

    return {"nodes": nodes, "edges": edges}


def _make_threat_actor_profile(actor: dict[str, Any]) -> dict[str, Any]:
    """
    Threat actor profile card grid.
    actor: {name, aliases, motivation, origin, ttps, iocs, campaigns, notes}
    """
    _reset_counter()
    nodes: list[dict] = []

    sections = [
        ("Overview", f"# {actor.get('name', 'Unknown')}\n\n**Aliases:** {', '.join(actor.get('aliases', []))}\n\n**Motivation:** {actor.get('motivation', 'Unknown')}\n\n**Origin:** {actor.get('origin', 'Unknown')}", "6"),
        ("TTPs", "## TTPs\n\n" + "\n".join(f"- {t}" for t in actor.get("ttps", [])), "3"),
        ("IOCs", "## IOCs\n\n" + "\n".join(f"- {i}" for i in actor.get("iocs", [])), "5"),
        ("Campaigns", "## Campaigns\n\n" + "\n".join(f"- {c}" for c in actor.get("campaigns", [])), "4"),
        ("Notes", "## Analyst Notes\n\n" + actor.get("notes", ""), "2"),
    ]

    positions = [(0, 0, 400, 240), (0, 280, 400, 240), (440, 0, 400, 240), (440, 280, 400, 240), (0, 560, 840, 120)]
    for i, (label, text, color) in enumerate(sections):
        if i >= len(positions):
            break
        x, y, w, h = positions[i]
        nodes.append({"id": _gen_id("section", label), "type": "text",
                      "x": x, "y": y, "width": w, "height": h,
                      "text": text, "color": color})

    return {"nodes": nodes, "edges": []}


# ── CanvasGenerator public API ─────────────────────────────────────────────────

class CanvasGenerator:
    """
    Generate Obsidian Canvas files for forensic investigations.

    Supports all 12 claude-canvas archetypes plus 6 forensic-specific ones:
    - attack-graph   — MITRE kill chain with sequential edges
    - ioc-map        — IOC network with type-color zones
    - timeline       — Incident timeline (horizontal)
    - threat-actor   — Threat actor profile card grid
    - network-topo   — Host/IP network topology
    - kill-chain     — 7-stage MITRE kill chain framework
    """

    STANDARD_ARCHETYPES = [
        "presentation", "flowchart", "mind-map", "gallery", "dashboard",
        "storyboard", "vector_rag-graph", "mood-board", "timeline",
        "comparison", "kanban", "project-brief",
    ]

    FORENSIC_ARCHETYPES = [
        "attack-graph", "ioc-map", "incident-timeline", "threat-actor",
        "network-topo", "kill-chain",
    ]

    def __init__(self, vault_path: str | Path = "./data/vault") -> None:
        self.vault_path = Path(vault_path).resolve()
        self.canvas_dir = self.vault_path / "wiki" / "canvases"
        self.canvas_dir.mkdir(parents=True, exist_ok=True)

    def create(
        self,
        archetype: str,
        title: str,
        output_name: str | None = None,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate a canvas file.

        For standard archetypes: uses template engine.
        For forensic archetypes: uses data dict with domain-specific builder.

        Returns: {"success": bool, "path": str, "nodes": int, "edges": int}
        """
        params = params or {}
        data = data or {}
        out_name = output_name or f"{title.lower().replace(' ', '-')}.canvas"
        output_path = self.canvas_dir / out_name

        if archetype in self.STANDARD_ARCHETYPES:
            return _instantiate(archetype, {"title": title, **params}, output_path)

        if archetype == "attack-graph":
            canvas = _make_attack_graph(title, data.get("stages", []))
        elif archetype == "ioc-map":
            canvas = _make_ioc_map(title, data.get("iocs", []))
        elif archetype == "incident-timeline":
            canvas = _make_timeline(title, data.get("events", []))
        elif archetype == "threat-actor":
            canvas = _make_threat_actor_profile(data.get("actor", {"name": title}))
        elif archetype == "kill-chain":
            stages = [
                {"name": "Reconnaissance", "technique": "TA0043", "detail": data.get("recon", "")},
                {"name": "Weaponization", "technique": "TA0001", "detail": data.get("weaponize", "")},
                {"name": "Delivery", "technique": "TA0001", "detail": data.get("delivery", "")},
                {"name": "Exploitation", "technique": "TA0002", "detail": data.get("exploit", "")},
                {"name": "Installation", "technique": "TA0003", "detail": data.get("install", "")},
                {"name": "C2", "technique": "TA0011", "detail": data.get("c2", "")},
                {"name": "Actions on Objectives", "technique": "TA0010", "detail": data.get("actions", "")},
            ]
            canvas = _make_attack_graph(title, stages)
        elif archetype == "network-topo":
            # Reuse ioc-map structure with host/IP types
            canvas = _make_ioc_map(title, [
                {"type": "host", "value": h.get("name", h.get("ip", "?")), "note": h.get("role", "")}
                for h in data.get("hosts", [])
            ])
        else:
            return {"success": False, "error": f"Unknown archetype: {archetype}"}

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(canvas, indent=2) + "\n", encoding="utf-8")
        return {
            "success": True, "archetype": archetype, "path": str(output_path),
            "nodes": len(canvas["nodes"]), "edges": len(canvas["edges"]),
        }

    def list(self) -> list[dict[str, Any]]:
        """List all canvas files with node counts."""
        result = []
        for f in sorted(self.canvas_dir.glob("*.canvas")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                nodes = data.get("nodes", [])
                result.append({
                    "name": f.name,
                    "path": str(f),
                    "nodes": len(nodes),
                    "edges": len(data.get("edges", [])),
                    "text_nodes": sum(1 for n in nodes if n.get("type") == "text"),
                    "image_nodes": sum(1 for n in nodes if n.get("type") == "file"),
                    "groups": sum(1 for n in nodes if n.get("type") == "group"),
                })
            except Exception:
                result.append({"name": f.name, "error": "invalid JSON"})
        return result

    def layout(self, canvas_name: str, algorithm: str) -> dict[str, Any]:
        """Re-layout an existing canvas with the specified algorithm."""
        canvas_path = self.canvas_dir / canvas_name
        if not canvas_path.exists():
            return {"success": False, "error": f"Canvas {canvas_name} not found"}

        try:
            data = json.loads(canvas_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON: {e}"}

        nodes = _apply_layout(data.get("nodes", []), data.get("edges", []), algorithm)
        data["nodes"] = nodes
        canvas_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return {"success": True, "canvas": canvas_name, "algorithm": algorithm, "nodes": len(nodes)}

    def add_node(
        self,
        canvas_name: str,
        node_type: str,
        content: str,
        x: int = 0,
        y: int = 0,
        width: int = 300,
        height: int = 120,
        color: str | None = None,
    ) -> dict[str, Any]:
        """Add a node to an existing canvas."""
        canvas_path = self.canvas_dir / canvas_name
        if not canvas_path.exists():
            return {"success": False, "error": f"Canvas {canvas_name} not found"}

        data = json.loads(canvas_path.read_text(encoding="utf-8"))
        nid = _gen_id(node_type[:4])
        node: dict[str, Any] = {
            "id": nid, "type": node_type, "x": x, "y": y,
            "width": width, "height": height,
        }
        if node_type == "text":
            node["text"] = content
        elif node_type == "file":
            node["file"] = content
        elif node_type == "link":
            node["url"] = content
        elif node_type == "group":
            node["label"] = content
        if color:
            node["color"] = color

        data.setdefault("nodes", []).append(node)
        canvas_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return {"success": True, "node_id": nid, "canvas": canvas_name}

    def validate(self, canvas_name: str) -> dict[str, Any]:
        """Validate canvas JSON structure."""
        canvas_path = self.canvas_dir / canvas_name
        if not canvas_path.exists():
            return {"valid": False, "error": f"Canvas {canvas_name} not found"}
        try:
            data = json.loads(canvas_path.read_text(encoding="utf-8"))
            node_ids = {n["id"] for n in data.get("nodes", [])}
            issues = []
            for edge in data.get("edges", []):
                if edge.get("fromNode") not in node_ids:
                    issues.append(f"Edge {edge.get('id')} references unknown fromNode {edge.get('fromNode')}")
                if edge.get("toNode") not in node_ids:
                    issues.append(f"Edge {edge.get('id')} references unknown toNode {edge.get('toNode')}")
            return {
                "valid": len(issues) == 0,
                "canvas": canvas_name,
                "nodes": len(data.get("nodes", [])),
                "edges": len(data.get("edges", [])),
                "issues": issues,
            }
        except json.JSONDecodeError as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def list_archetypes() -> dict[str, list[str]]:
        return {
            "standard": CanvasGenerator.STANDARD_ARCHETYPES,
            "forensic": CanvasGenerator.FORENSIC_ARCHETYPES,
        }
