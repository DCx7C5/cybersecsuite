"""PoC (Proof of Concept) MCP tools."""
from __future__ import annotations

from typing import Any

from ..sdk_compat import tool
from ..helpers import JsonDict, sdk_result, sdk_error


@tool(
    "query_pocs",
    "Query PoC exploit records, optionally filtered by CVE ID, status, or weaponized flag.",
    {
        "cve_id": {"type": "string", "description": "Filter by CVE ID (e.g. CVE-2021-44228). Optional."},
        "status": {"type": "string", "description": "Filter by status: unverified|verified|weaponized|patched|disputed. Optional."},
        "weaponized_only": {"type": "boolean", "description": "If true, return only weaponized PoCs. Optional."},
        "limit": {"type": "integer", "description": "Max results (default 20, max 100)."},
    },
)
async def query_pocs(args: dict[str, Any]) -> JsonDict:
    try:
        from db.models.poc import ProofOfConcept
    except ImportError:
        return sdk_error("db.models.poc not available — ensure src/ is in PYTHONPATH")

    cve_id = args.get("cve_id", "").strip()
    status = args.get("status", "").strip()
    weaponized = args.get("weaponized_only", False)
    limit = min(int(args.get("limit", 20)), 100)

    qs = ProofOfConcept.all().prefetch_related("cve")
    if cve_id:
        qs = qs.filter(cve__cve_id=cve_id)
    if status:
        qs = qs.filter(status=status)
    if weaponized:
        qs = qs.filter(is_weaponized=True)

    pocs = await qs.limit(limit)
    return sdk_result({
        "count": len(pocs),
        "pocs": [
            {
                "id": p.id,
                "title": p.title,
                "cve_id": p.cve.cve_id if p.cve_id and p.cve else None,
                "status": p.status,
                "severity": p.severity,
                "poc_url": p.poc_url,
                "source": p.source,
                "language": p.language,
                "is_weaponized": p.is_weaponized,
                "reliability_score": p.reliability_score,
                "requires_auth": p.requires_auth,
                "tags": p.tags,
            }
            for p in pocs
        ],
    })


@tool(
    "add_poc",
    "Add a new PoC exploit record linked to a CVE.",
    {
        "cve_id": {"type": "string", "description": "CVE ID to link (e.g. CVE-2021-44228)."},
        "title": {"type": "string", "description": "PoC title."},
        "poc_url": {"type": "string", "description": "URL to the PoC/exploit."},
        "source": {"type": "string", "description": "Source (GitHub, ExploitDB, PacketStorm, …)."},
        "language": {"type": "string", "description": "Primary programming language."},
        "status": {"type": "string", "description": "unverified|verified|weaponized|patched|disputed."},
        "is_weaponized": {"type": "boolean", "description": "True if actively weaponized."},
        "description": {"type": "string", "description": "Detailed description."},
        "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags."},
    },
)
async def add_poc(args: dict[str, Any]) -> JsonDict:
    try:
        from db.models.poc import ProofOfConcept
        from db.models.cve import CVEIntel
        from db.models.enums import PocStatus
    except ImportError:
        return sdk_error("db.models.poc not available — ensure src/ is in PYTHONPATH")

    cve_id = args.get("cve_id", "").strip()
    cve = await CVEIntel.filter(cve_id=cve_id).first() if cve_id else None

    poc = await ProofOfConcept.create(
        cve=cve,
        title=args.get("title", ""),
        poc_url=args.get("poc_url", ""),
        source=args.get("source", ""),
        language=args.get("language", ""),
        status=PocStatus(args.get("status", "unverified")),
        is_weaponized=bool(args.get("is_weaponized", False)),
        description=args.get("description", ""),
        tags=args.get("tags", []),
    )
    return sdk_result({"id": poc.id, "title": poc.title, "status": poc.status})


ALL_TOOLS = [query_pocs, add_poc]
