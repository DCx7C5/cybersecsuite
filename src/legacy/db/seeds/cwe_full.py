"""
CWE (Common Weakness Enumeration) full seeding — fetches from MITRE API.

CWE API: https://cwe.mitre.org/data/json/
Downloads full CWE list as JSON.  Results are cached to data/fixtures/cwe_full.json
so subsequent runs skip the network request.
"""


import json
import logging
from pathlib import Path

import httpx

from db.models.cwe import CWEIntel

logger = logging.getLogger("db.seeds.cwe_full")

CWE_JSON_URL = "https://raw.githubusercontent.com/mitre/cwe-csv2/master/cwe.json"

_CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "fixtures"
_CACHE_FILE = _CACHE_DIR / "cwe_full.json"


def _parse_cwe_item(item: dict) -> dict:
    """Map raw CWE API item to CWEIntel field dict."""
    cwe_id = item.get("id", "")
    if not cwe_id.startswith("CWE-"):
        cwe_id = f"CWE-{cwe_id}"
    related = []
    for r in item.get("related_weaknesses", []):
        rid = r.get("cwe_id", "")
        if rid and not rid.startswith("CWE-"):
            rid = f"CWE-{rid}"
        if rid:
            related.append(rid)
    consequences = item.get("common_consequences", [])
    if isinstance(consequences, list) and consequences and isinstance(consequences[0], dict):
        consequences = [c.get("scope", "") for c in consequences if c.get("scope")]
    return {
        "cwe_id": cwe_id,
        "name": item.get("name", ""),
        "abstraction": item.get("abstraction", item.get("type", "")),
        "status": item.get("status", ""),
        "description": item.get("description", ""),
        "likelihood_of_exploit": item.get("likelihood_of_exploit", ""),
        "common_consequences": consequences,
        "tags": related,
    }


async def seed_cwe_full(max_results: int | None = None) -> tuple[int, int]:
    """
    Seed all CWEs from MITRE JSON source.  Loads from local cache if available,
    otherwise fetches from API and saves to cache.

    Returns:
        (total_created, total_synced) tuple
    """
    records: list[dict] = []

    if _CACHE_FILE.exists():
        logger.info(f"Loading CWE from cache: {_CACHE_FILE}")
        records = json.loads(_CACHE_FILE.read_text())
    else:
        logger.info("Fetching full CWE list from MITRE")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(CWE_JSON_URL)
                if resp.status_code != 200:
                    logger.error(f"CWE fetch failed: {resp.status_code}")
                    return 0, 0
                raw_list = resp.json().get("weakness_list", [])
        except Exception as exc:
            logger.error(f"CWE fetch error: {exc}")
            return 0, 0

        records = [_parse_cwe_item(item) for item in raw_list]
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2))
        logger.info(f"Cached {len(records)} CWEs → {_CACHE_FILE}")

    if max_results:
        records = records[:max_results]

    total_created = total_synced = 0
    for rec in records:
        try:
            cwe_id = rec.pop("cwe_id")
            _, created = await CWEIntel.get_or_create(cwe_id=cwe_id, defaults=rec)
            rec["cwe_id"] = cwe_id  # restore for next iteration safety
            if created:
                total_created += 1
            total_synced += 1
        except Exception as exc:
            logger.error(f"Failed to insert CWE {rec.get('cwe_id')}: {exc}")

    logger.info(f"CWE seed complete: created={total_created}, total={total_synced}")
    return total_created, total_synced

