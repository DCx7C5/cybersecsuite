"""
MITRE ATT&CK full seeding — fetches techniques, actors, and software from MITRE.

MITRE ATT&CK API: https://attack.mitre.org/
Downloads full ATT&CK framework data as JSON.
"""
from __future__ import annotations

import json
import logging

import httpx

from db.models.mitre_technique import MITRETechnique
from db.models.mitre_actor import MITREActor
from db.models.mitre_software import MITRESoftware

logger = logging.getLogger("db.seeds.mitre_full")

# MITRE ATT&CK GitHub enterprise JSON
MITRE_ENTERPRISE_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"


async def seed_mitre_full(
    max_results: int | None = None,
) -> dict[str, int]:
    """
    Seed all MITRE ATT&CK data (techniques, actors, software).

    Args:
        max_results: Limit per category (default: all)

    Returns:
        Dict with {techniques_created, techniques_total, actors_created, actors_total, ...}
    """
    results = {
        "techniques_created": 0,
        "techniques_total": 0,
        "actors_created": 0,
        "actors_total": 0,
        "software_created": 0,
        "software_total": 0,
    }

    logger.info("Starting full MITRE ATT&CK seed")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(MITRE_ENTERPRISE_URL)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch MITRE data: {resp.status_code}")
                return results

            data = resp.json()
            objects = data.get("objects", [])

            logger.info(f"Fetched {len(objects)} MITRE objects")

            # Process objects by type
            for obj in objects:
                obj_type = obj.get("type", "")

                # Seed techniques (attack-pattern)
                if obj_type == "attack-pattern":
                    technique_id = None
                    for ext_ref in obj.get("external_references", []):
                        if ext_ref.get("source_name") == "mitre-attack":
                            technique_id = ext_ref.get("external_id")
                            break

                    if not technique_id:
                        continue

                    name = obj.get("name", "")
                    description = obj.get("description", "")
                    tactics = [
                        tactic.replace("-", " ").title()
                        for tactic in obj.get("kill_chain_phases", [{}])[0].get("phase_name", "").split() if tactic
                    ] or []

                    try:
                        tech_record, created = await MITRETechnique.get_or_create(
                            technique_id=technique_id,
                            defaults={
                                "name": name,
                                "description": description,
                                "tactics": tactics,
                                "raw_mitre_data": obj,
                            },
                        )
                        if created:
                            results["techniques_created"] += 1
                        results["techniques_total"] += 1

                        if max_results and results["techniques_total"] >= max_results:
                            logger.info(f"Reached max techniques limit")
                            break

                    except Exception as e:
                        logger.error(f"Failed to insert technique {technique_id}: {e}")

                # Seed threat actors (intrusion-set)
                elif obj_type == "intrusion-set":
                    name = obj.get("name", "")
                    description = obj.get("description", "")

                    # Get external ID
                    actor_id = None
                    for ext_ref in obj.get("external_references", []):
                        if ext_ref.get("source_name") == "mitre-attack":
                            actor_id = ext_ref.get("external_id")
                            break

                    if not actor_id:
                        actor_id = obj.get("id", "").replace("intrusion-set--", "G")

                    aliases = obj.get("aliases", [])

                    try:
                        actor_record, created = await MITREActor.get_or_create(
                            actor_id=actor_id,
                            defaults={
                                "name": name,
                                "description": description,
                                "aliases": aliases,
                                "raw_mitre_data": obj,
                            },
                        )
                        if created:
                            results["actors_created"] += 1
                        results["actors_total"] += 1

                        if max_results and results["actors_total"] >= max_results:
                            logger.info(f"Reached max actors limit")
                            break

                    except Exception as e:
                        logger.error(f"Failed to insert actor {actor_id}: {e}")

                # Seed software/malware/tools (malware, tool)
                elif obj_type in ("malware", "tool"):
                    software_id = None
                    for ext_ref in obj.get("external_references", []):
                        if ext_ref.get("source_name") == "mitre-attack":
                            software_id = ext_ref.get("external_id")
                            break

                    if not software_id:
                        software_id = obj.get("id", "").replace("malware--", "S").replace("tool--", "S")

                    name = obj.get("name", "")
                    description = obj.get("description", "")
                    software_type = obj_type.capitalize()
                    aliases = obj.get("aliases", [])

                    try:
                        soft_record, created = await MITRESoftware.get_or_create(
                            software_id=software_id,
                            defaults={
                                "name": name,
                                "description": description,
                                "software_type": software_type,
                                "aliases": aliases,
                                "raw_mitre_data": obj,
                            },
                        )
                        if created:
                            results["software_created"] += 1
                        results["software_total"] += 1

                        if max_results and results["software_total"] >= max_results:
                            logger.info(f"Reached max software limit")
                            break

                    except Exception as e:
                        logger.error(f"Failed to insert software {software_id}: {e}")

    except Exception as e:
        logger.error(f"MITRE seeding failed: {e}")
        return results

    logger.info(
        f"MITRE seed complete: "
        f"techniques={results['techniques_created']}/{results['techniques_total']}, "
        f"actors={results['actors_created']}/{results['actors_total']}, "
        f"software={results['software_created']}/{results['software_total']}"
    )
    return results

