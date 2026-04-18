"""
CAPEC (Common Attack Pattern Expression Language) full seeding — fetches from MITRE.

Results are cached to data/fixtures/capec_full.json so subsequent runs skip the
network request.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx

from db.models.capec import CapecAttackPatternIntel

logger = logging.getLogger("db.seeds.capec_full")

CAPEC_JSON_URL = "https://raw.githubusercontent.com/mitre/capec/master/capec.json"

_CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "fixtures"
_CACHE_FILE = _CACHE_DIR / "capec_full.json"


def _parse_capec_item(item: dict) -> dict:
    """Map raw CAPEC API item to CapecAttackPatternIntel field dict."""
    capec_id = item.get("id", "")
    if not capec_id.startswith("CAPEC-"):
        capec_id = f"CAPEC-{capec_id}"
    related_weaknesses = []
    for rel in item.get("related_weaknesses", []):
        cwe_id = rel.get("cwe_id", "")
        if cwe_id and not cwe_id.startswith("CWE-"):
            cwe_id = f"CWE-{cwe_id}"
        if cwe_id:
            related_weaknesses.append(cwe_id)
    return {
        "capec_id": capec_id,
        "name": item.get("name", ""),
        "description": item.get("description", ""),
        "abstraction": item.get("abstraction", ""),
        "domains": item.get("domains", item.get("execution_flow", [])),
        "likelihood_of_attack": item.get("likelihood_of_attack", ""),
        "severity": item.get("severity", item.get("typical_severity", "")),
        "url": item.get("url", ""),
        "tags": related_weaknesses,
    }


async def seed_capec_full(max_results: int | None = None) -> tuple[int, int]:
    """
    Seed all CAPEC attack patterns from MITRE.  Loads from local cache if available,
    otherwise fetches from API and saves to cache.

    Returns:
        (total_created, total_synced) tuple
    """
    records: list[dict] = []

    if _CACHE_FILE.exists():
        logger.info(f"Loading CAPEC from cache: {_CACHE_FILE}")
        records = json.loads(_CACHE_FILE.read_text())
    else:
        logger.info("Fetching full CAPEC list from MITRE")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(CAPEC_JSON_URL)
                if resp.status_code != 200:
                    logger.error(f"CAPEC fetch failed: {resp.status_code}")
                    return 0, 0
                raw_list = resp.json().get("attack_patterns", [])
        except Exception as exc:
            logger.error(f"CAPEC fetch error: {exc}")
            return 0, 0

        records = [_parse_capec_item(item) for item in raw_list]
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2))
        logger.info(f"Cached {len(records)} CAPEC patterns → {_CACHE_FILE}")

    if max_results:
        records = records[:max_results]

    total_created = total_synced = 0
    for rec in records:
        try:
            capec_id = rec.pop("capec_id")
            _, created = await CapecAttackPatternIntel.get_or_create(capec_id=capec_id, defaults=rec)
            rec["capec_id"] = capec_id
            if created:
                total_created += 1
            total_synced += 1
        except Exception as exc:
            logger.error(f"Failed to insert CAPEC {rec.get('capec_id')}: {exc}")

    logger.info(f"CAPEC seed complete: created={total_created}, total={total_synced}")
    return total_created, total_synced

