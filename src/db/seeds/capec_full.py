"""
CAPEC (Common Attack Pattern Expression Language) full seeding — fetches from MITRE.

CAPEC API: https://capec.mitre.org/
Downloads full CAPEC patterns as XML/JSON.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from db.models.capec import CAPEC

logger = logging.getLogger("db.seeds.capec_full")

# MITRE CAPEC GitHub raw JSON
CAPEC_JSON_URL = "https://raw.githubusercontent.com/mitre/capec/master/capec.json"


async def seed_capec_full(
    max_results: int | None = None,
) -> tuple[int, int]:
    """
    Seed all CAPEC attack patterns from MITRE.

    Args:
        max_results: Limit total CAPECs (default: all)

    Returns:
        (total_created, total_synced) tuple
    """
    total_created = 0
    total_synced = 0

    logger.info("Starting full CAPEC seed")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(CAPEC_JSON_URL)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch CAPEC JSON: {resp.status_code}")
                return (0, 0)

            data = resp.json()
            capec_list = data.get("attack_patterns", [])

            logger.info(f"Fetched {len(capec_list)} CAPEC patterns from MITRE")

            for capec_item in capec_list:
                capec_id = capec_item.get("id", "")
                if not capec_id.startswith("CAPEC-"):
                    capec_id = f"CAPEC-{capec_id}"

                name = capec_item.get("name", "")
                description = capec_item.get("description", "")
                severity = capec_item.get("severity", "Medium")

                # Extract prerequisites and consequences
                prerequisites = capec_item.get("prerequisites", [])
                consequences = capec_item.get("consequences", [])

                # Extract related weaknesses (CWEs)
                related_weaknesses = []
                for rel in capec_item.get("related_weaknesses", []):
                    cwe_id = rel.get("cwe_id", "")
                    if cwe_id and not cwe_id.startswith("CWE-"):
                        cwe_id = f"CWE-{cwe_id}"
                    if cwe_id:
                        related_weaknesses.append(cwe_id)

                try:
                    capec_record, created = await CAPEC.get_or_create(
                        capec_id=capec_id,
                        defaults={
                            "name": name,
                            "description": description,
                            "severity": severity,
                            "prerequisites": prerequisites,
                            "consequences": consequences,
                            "related_weaknesses": related_weaknesses,
                            "mitre_data": capec_item,
                        },
                    )
                    if created:
                        total_created += 1
                    total_synced += 1

                    if max_results and total_synced >= max_results:
                        logger.info(f"Reached max_results limit ({max_results})")
                        break

                except Exception as e:
                    logger.error(f"Failed to insert CAPEC {capec_id}: {e}")

    except Exception as e:
        logger.error(f"CAPEC seeding failed: {e}")
        return 0, 0

    logger.info(f"CAPEC seed complete: created={total_created}, total={total_synced}")
    return total_created, total_synced

