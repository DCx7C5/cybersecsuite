"""
MITRE ATT&CK full seeding — fetches techniques, actors, and software from MITRE.

Results are cached to data/fixtures/mitre_techniques_full.json,
data/fixtures/mitre_actors_full.json, and data/fixtures/mitre_software_full.json
so subsequent runs skip the network request.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx

from db.models.mitre_technique import MitreTechniqueIntel
from db.models.mitre_actor import MitreThreatActorIntel
from db.models.mitre_software import MitreSoftwareFamilyIntel

logger = logging.getLogger("db.seeds.mitre_full")

MITRE_ENTERPRISE_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"

_CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "fixtures"
_CACHE_TECHNIQUES = _CACHE_DIR / "mitre_techniques_full.json"
_CACHE_ACTORS = _CACHE_DIR / "mitre_actors_full.json"
_CACHE_SOFTWARE = _CACHE_DIR / "mitre_software_full.json"


def _external_id(obj: dict, source: str = "mitre-attack") -> str | None:
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == source:
            return ref.get("external_id")
    return None


def _external_url(obj: dict, source: str = "mitre-attack") -> str:
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == source:
            return ref.get("url", "")
    return ""


def _parse_technique(obj: dict) -> dict | None:
    tid = _external_id(obj)
    if not tid:
        return None
    phases = obj.get("kill_chain_phases", [])
    tactics = list({p["phase_name"].replace("-", " ").title() for p in phases if "phase_name" in p})
    platforms = obj.get("x_mitre_platforms", [])
    parent_id = ""
    if "." in tid:
        parent_id = tid.split(".")[0]
    return {
        "technique_id": tid,
        "name": obj.get("name", ""),
        "tactics": tactics,
        "platforms": platforms,
        "is_sub_technique": "." in tid,
        "parent_technique_id": parent_id,
        "description": obj.get("description", ""),
        "detection": obj.get("x_mitre_detection", ""),
        "url": _external_url(obj),
        "tags": [],
    }


def _parse_actor(obj: dict) -> dict | None:
    name = obj.get("name", "")
    if not name:
        return None
    aid = _external_id(obj) or obj.get("id", "").replace("intrusion-set--", "G")
    return {
        "actor_name": name,
        "description": obj.get("description", ""),
        "aliases": obj.get("aliases", []),
        "country_of_origin": obj.get("x_mitre_attribution_country", ""),
        "motivation": obj.get("primary_motivation", ""),
        "target_sectors": obj.get("x_mitre_sectors", []),
        "target_regions": obj.get("x_mitre_regions", []),
        "tools_used": [],
        "url": _external_url(obj),
        "tags": [aid] if aid else [],
    }


def _parse_software(obj: dict) -> dict | None:
    sid = _external_id(obj)
    if not sid:
        raw_id = obj.get("id", "")
        sid = raw_id.replace("malware--", "S").replace("tool--", "S")
    return {
        "software_id": sid,
        "name": obj.get("name", ""),
        "software_type": obj.get("type", "").capitalize(),
        "description": obj.get("description", ""),
        "aliases": obj.get("aliases", []),
        "platforms": obj.get("x_mitre_platforms", []),
        "is_family": obj.get("type") == "malware",
        "url": _external_url(obj),
        "tags": [],
    }


async def seed_mitre_full(max_results: int | None = None) -> dict[str, int]:
    """
    Seed all MITRE ATT&CK data (techniques, actors, software).  Loads from local
    cache if all three cache files exist, otherwise fetches from API and saves.

    Returns:
        Dict with counts per category.
    """
    results = {
        "techniques_created": 0, "techniques_total": 0,
        "actors_created": 0, "actors_total": 0,
        "software_created": 0, "software_total": 0,
    }

    all_cached = _CACHE_TECHNIQUES.exists() and _CACHE_ACTORS.exists() and _CACHE_SOFTWARE.exists()

    if all_cached:
        logger.info("Loading MITRE ATT&CK from cache")
        techniques = json.loads(_CACHE_TECHNIQUES.read_text())
        actors = json.loads(_CACHE_ACTORS.read_text())
        software = json.loads(_CACHE_SOFTWARE.read_text())
    else:
        logger.info("Fetching MITRE ATT&CK enterprise JSON")
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.get(MITRE_ENTERPRISE_URL)
                if resp.status_code != 200:
                    logger.error(f"MITRE fetch failed: {resp.status_code}")
                    return results
                objects = resp.json().get("objects", [])
        except Exception as exc:
            logger.error(f"MITRE fetch error: {exc}")
            return results

        techniques = [r for obj in objects if obj.get("type") == "attack-pattern" if (r := _parse_technique(obj))]
        actors = [r for obj in objects if obj.get("type") == "intrusion-set" if (r := _parse_actor(obj))]
        software = [r for obj in objects if obj.get("type") in ("malware", "tool") if (r := _parse_software(obj))]

        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _CACHE_TECHNIQUES.write_text(json.dumps(techniques, ensure_ascii=False, indent=2))
        _CACHE_ACTORS.write_text(json.dumps(actors, ensure_ascii=False, indent=2))
        _CACHE_SOFTWARE.write_text(json.dumps(software, ensure_ascii=False, indent=2))
        logger.info(f"Cached {len(techniques)} techniques, {len(actors)} actors, {len(software)} software")

    if max_results:
        techniques = techniques[:max_results]
        actors = actors[:max_results]
        software = software[:max_results]

    for rec in techniques:
        try:
            tid = rec.pop("technique_id")
            _, created = await MitreTechniqueIntel.get_or_create(technique_id=tid, defaults=rec)
            rec["technique_id"] = tid
            results["techniques_created"] += created
            results["techniques_total"] += 1
        except Exception as exc:
            logger.error(f"Failed to insert technique {rec.get('technique_id')}: {exc}")

    for rec in actors:
        try:
            name = rec.pop("actor_name")
            _, created = await MitreThreatActorIntel.get_or_create(actor_name=name, defaults=rec)
            rec["actor_name"] = name
            results["actors_created"] += created
            results["actors_total"] += 1
        except Exception as exc:
            logger.error(f"Failed to insert actor {rec.get('actor_name')}: {exc}")

    for rec in software:
        try:
            sid = rec.pop("software_id")
            _, created = await MitreSoftwareFamilyIntel.get_or_create(software_id=sid, defaults=rec)
            rec["software_id"] = sid
            results["software_created"] += created
            results["software_total"] += 1
        except Exception as exc:
            logger.error(f"Failed to insert software {rec.get('software_id')}: {exc}")

    logger.info(
        f"MITRE seed complete: "
        f"techniques={results['techniques_created']}/{results['techniques_total']}, "
        f"actors={results['actors_created']}/{results['actors_total']}, "
        f"software={results['software_created']}/{results['software_total']}"
    )
    return results

