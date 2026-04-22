"""Flowgraph API — agent palette + pipeline executor."""
from __future__ import annotations

import pathlib

from starlette.requests import Request
from starlette.responses import JSONResponse

_AGENTS_DIR = pathlib.Path(".claude/agents")


def _scan_agents() -> list[dict]:
    """Return agent name + description from .claude/agents/*.md files."""
    agents = []
    if not _AGENTS_DIR.exists():
        return agents
    for md in sorted(_AGENTS_DIR.glob("*.md")):
        name = md.stem
        desc = ""
        try:
            text = md.read_text(errors="replace")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                    desc = stripped[:120]
                    break
        except OSError:
            pass
        agents.append({"name": name, "description": desc, "source": "claude-agents"})

    # Also include sub_agents subdirectory
    sub = _AGENTS_DIR / "sub_agents"
    if sub.exists():
        for md in sorted(sub.glob("*.md")):
            name = md.stem
            desc = ""
            try:
                text = md.read_text(errors="replace")
                for line in text.splitlines():
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                        desc = stripped[:120]
                        break
            except OSError:
                pass
            agents.append({"name": name, "description": desc, "source": "sub-agents"})
    return agents


async def api_flowgraph_agents(request: Request) -> JSONResponse:
    """GET /api/flowgraph/agents — list available agent nodes for palette."""
    agents = _scan_agents()
    return JSONResponse({"agents": agents, "total": len(agents)})


async def api_flowgraph_execute(request: Request) -> JSONResponse:
    """POST /api/flowgraph/execute — run a Drawflow JSON graph as a pipeline.

    Accepts: { "graph": <Drawflow export JSON> }
    Returns: { "run_id": str, "nodes_executed": int, "results": {node_id: text} }

    Phase 1: sequential topological execution (SSE streaming in phase 2).
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    graph = body.get("graph", {})
    if not graph:
        return JSONResponse({"error": "No graph provided"}, status_code=400)

    # Extract nodes from Drawflow export format
    # Drawflow JSON: { drawflow: { Home: { data: { "1": { name, data, inputs, outputs, ... } } } } }
    try:
        modules = graph.get("drawflow", {})
        all_nodes: dict[str, dict] = {}
        for module_data in modules.values():
            all_nodes.update(module_data.get("data", {}))
    except Exception as exc:
        return JSONResponse({"error": f"Malformed graph: {exc}"}, status_code=400)

    if not all_nodes:
        return JSONResponse({"error": "Graph has no nodes"}, status_code=400)

    # Build adjacency for topological sort
    adj: dict[str, list[str]] = {nid: [] for nid in all_nodes}
    for nid, node in all_nodes.items():
        for out_port in node.get("outputs", {}).values():
            for conn in out_port.get("connections", []):
                target = str(conn.get("node", ""))
                if target and target in adj:
                    adj[nid].append(target)

    order = _topological_sort(adj)

    import uuid
    run_id = str(uuid.uuid4())[:8]
    results: dict[str, str] = {}
    nodes_executed = 0

    for nid in order:
        node = all_nodes.get(nid, {})
        node_type = node.get("name", "unknown")
        node_data = node.get("data", {})
        label = node_data.get("label", node_type)

        if node_type == "agent":
            result = await _execute_agent_node(label, node_data, results)
        elif node_type == "mcp-tool":
            result = f"[mcp-tool:{label}] — tool execution not yet wired (phase 2)"
        elif node_type == "condition":
            result = "[condition] — always true (phase 2 adds evaluation)"
        elif node_type == "merge":
            # Collect all upstream results
            upstream = [results.get(src) for src in _upstream_nodes(nid, adj) if src in results]
            result = "\n---\n".join(filter(None, upstream)) or "(no upstream results)"
        elif node_type == "output":
            upstream = [results.get(src) for src in _upstream_nodes(nid, adj) if src in results]
            result = upstream[-1] if upstream else "(no input)"
        else:
            result = f"[{node_type}] unknown node type"

        results[nid] = result
        nodes_executed += 1

    return JSONResponse({
        "run_id": run_id,
        "nodes_executed": nodes_executed,
        "results": results,
        "order": order,
    })


# ── Helpers ───────────────────────────────────────────────────────────────────

def _topological_sort(adj: dict[str, list[str]]) -> list[str]:
    """Kahn's algorithm — returns nodes in execution order."""
    in_degree = {nid: 0 for nid in adj}
    for deps in adj.values():
        for d in deps:
            in_degree[d] = in_degree.get(d, 0) + 1
    queue = [nid for nid, deg in in_degree.items() if deg == 0]
    order: list[str] = []
    while queue:
        cur = queue.pop(0)
        order.append(cur)
        for nxt in adj.get(cur, []):
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)
    # Append any remaining nodes (cycles fallback)
    for nid in adj:
        if nid not in order:
            order.append(nid)
    return order


def _upstream_nodes(target: str, adj: dict[str, list[str]]) -> list[str]:
    return [src for src, dsts in adj.items() if target in dsts]


async def _execute_agent_node(label: str, data: dict, prior_results: dict[str, str]) -> str:
    """Run an agent node via the A2A endpoint (best-effort; fails gracefully)."""
    prompt = data.get("prompt", "Summarise findings so far.")
    # Inject prior pipeline results as context
    context_text = "\n\n".join(v for v in prior_results.values() if v)
    if context_text:
        prompt = f"Context from previous pipeline steps:\n{context_text}\n\n{prompt}"
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "http://localhost:8000/a2a/run",
                json={"agent": label, "prompt": prompt},
            )
            if resp.status_code == 200:
                body = resp.json()
                return body.get("result", body.get("output", str(body)))
            return f"[{label}] HTTP {resp.status_code}"
    except Exception as exc:
        return f"[{label}] error: {exc}"
