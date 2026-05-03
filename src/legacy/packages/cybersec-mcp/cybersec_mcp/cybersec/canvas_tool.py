"""
Canvas MCP tools — create, list, layout, validate, add_node.

Wraps CanvasGenerator to generate Obsidian Canvas files for forensic use cases.
"""
from __future__ import annotations

import os
from typing import Any

from ..helpers import JsonDict, sdk_error, sdk_result
from ..sdk_compat import tool

_VAULT_PATH = os.getenv("CYBERSEC_VAULT_PATH", "./data/vault")


def _get_gen():
    from memory.canvas.generator import CanvasGenerator
    return CanvasGenerator(_VAULT_PATH)


@tool(
    "canvas_create",
    "Create an Obsidian Canvas file. Standard archetypes: presentation, flowchart, mind-map, gallery, dashboard, storyboard, knowledge-graph, comparison, kanban, project-brief. Forensic: attack-graph, ioc-map, incident-timeline, threat-actor, network-topo, kill-chain.",
    {
        "archetype": {
            "type": "string",
            "description": "Canvas archetype to generate",
            "enum": [
                "presentation", "flowchart", "mind-map", "gallery", "dashboard",
                "storyboard", "knowledge-graph", "mood-board", "timeline",
                "comparison", "kanban", "project-brief",
                "attack-graph", "ioc-map", "incident-timeline", "threat-actor",
                "network-topo", "kill-chain",
            ],
        },
        "title": {"type": "string", "description": "Canvas title"},
        "output_name": {"type": "string", "description": "Output filename (without path). Defaults to title-based slug."},
        "params": {"type": "object", "description": "Template parameters (color_title, color_body, color_accent, item_count, etc.)"},
        "data": {"type": "object", "description": "Domain data for forensic archetypes. attack-graph: {stages:[{name,technique,detail}]}. ioc-map: {iocs:[{type,value,note}]}. incident-timeline: {events:[{date,event,severity}]}. threat-actor: {actor:{name,aliases,motivation,origin,ttps,iocs,campaigns,notes}}. network-topo: {hosts:[{name,ip,role}]}. kill-chain: {recon,weaponize,delivery,exploit,install,c2,actions}."},
    },
)
async def canvas_create(args: dict[str, Any]) -> JsonDict:
    archetype = args.get("archetype", "")
    title = args.get("title", "Untitled")
    output_name = args.get("output_name")
    params = args.get("params") or {}
    data = args.get("data") or {}

    if not archetype:
        return sdk_error("'archetype' is required")

    try:
        gen = _get_gen()
        result = gen.create(archetype, title, output_name=output_name, params=params, data=data)
        return sdk_result(result)
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "canvas_list",
    "List all Obsidian Canvas files in the vault with node/edge counts.",
    {},
)
async def canvas_list(args: dict[str, Any]) -> JsonDict:
    try:
        gen = _get_gen()
        canvases = gen.list()
        return sdk_result({"canvases": canvases, "count": len(canvases)})
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "canvas_layout",
    "Re-layout an existing canvas with a different algorithm.",
    {
        "canvas_name": {"type": "string", "description": "Canvas filename (e.g. attack-graph.canvas)"},
        "algorithm": {
            "type": "string",
            "enum": ["grid", "dagre", "radial", "linear-vertical", "linear-horizontal"],
            "description": "Layout algorithm to apply",
        },
    },
)
async def canvas_layout(args: dict[str, Any]) -> JsonDict:
    canvas_name = args.get("canvas_name", "")
    algorithm = args.get("algorithm", "grid")
    if not canvas_name:
        return sdk_error("'canvas_name' is required")
    try:
        gen = _get_gen()
        return sdk_result(gen.layout(canvas_name, algorithm))
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "canvas_add_node",
    "Add a node to an existing canvas.",
    {
        "canvas_name": {"type": "string", "description": "Canvas filename"},
        "node_type": {
            "type": "string",
            "enum": ["text", "file", "link", "group"],
            "default": "text",
        },
        "content": {"type": "string", "description": "Node content: markdown text, file path, URL, or group label"},
        "x": {"type": "integer", "default": 0},
        "y": {"type": "integer", "default": 0},
        "width": {"type": "integer", "default": 300},
        "height": {"type": "integer", "default": 120},
        "color": {"type": "string", "description": "Obsidian color (1=red, 2=orange, 3=yellow, 4=green, 5=teal, 6=purple)"},
    },
)
async def canvas_add_node(args: dict[str, Any]) -> JsonDict:
    canvas_name = args.get("canvas_name", "")
    if not canvas_name:
        return sdk_error("'canvas_name' is required")
    try:
        gen = _get_gen()
        result = gen.add_node(
            canvas_name,
            args.get("node_type", "text"),
            args.get("content", ""),
            x=int(args.get("x", 0)),
            y=int(args.get("y", 0)),
            width=int(args.get("width", 300)),
            height=int(args.get("height", 120)),
            color=args.get("color"),
        )
        return sdk_result(result)
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "canvas_validate",
    "Validate canvas JSON structure (checks edge node references).",
    {
        "canvas_name": {"type": "string", "description": "Canvas filename to validate"},
    },
)
async def canvas_validate(args: dict[str, Any]) -> JsonDict:
    canvas_name = args.get("canvas_name", "")
    if not canvas_name:
        return sdk_error("'canvas_name' is required")
    try:
        gen = _get_gen()
        return sdk_result(gen.validate(canvas_name))
    except Exception as e:
        return sdk_error(str(e))


@tool(
    "canvas_archetypes",
    "List all available canvas archetypes (standard + forensic).",
    {},
)
async def canvas_archetypes(args: dict[str, Any]) -> JsonDict:
    from memory.canvas.generator import CanvasGenerator
    return sdk_result(CanvasGenerator.list_archetypes())

ALL_TOOLS = [canvas_create, canvas_list, canvas_layout, canvas_add_node, canvas_validate, canvas_archetypes]
