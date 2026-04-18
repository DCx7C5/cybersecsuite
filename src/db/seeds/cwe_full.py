"""
CWE (Common Weakness Enumeration) full seeding — fetches from MITRE API.

CWE API: https://cwe.mitre.org/data/json/
Downloads full CWE list as JSON.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import httpx

from db.models.cwe import CWE

logger = logging.getLogger("db.seeds.cwe_full")

CWE_API_URL = "https://cwe.mitre.org/data/json/cwe.json.zip"
CWE_JSON_URL = "https://raw.githubusercontent.com/mitre/cwe-csv2/master/cwe.json"


async def seed_cwe_full(
    max_results: int | None = None,
) -> tuple[int, int]:
    """
    Seed all CWEs from MITRE JSON source.

    Args:
        max_results: Limit total CWEs (default: all)

    Returns:
        (total_created, total_synced) tuple
    """
    total_created = 0
    total_synced = 0

    logger.info("Starting full CWE seed")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(CWE_JSON_URL)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch CWE JSON: {resp.status_code}")
                return (0, 0)

            data = resp.json()
            cwe_list = data.get("weakness_list", [])

            logger.info(f"Fetched {len(cwe_list)} CWEs from MITRE")

            for cwe_item in cwe_list:
                cwe_id = cwe_item.get("id", "")
                if not cwe_id.startswith("CWE-"):
                    cwe_id = f"CWE-{cwe_id}"

                name = cwe_item.get("name", "")
                description = cwe_item.get("description", "")
                category = cwe_item.get("type", "Weakness")

                # Extract related
                related_weaknesses = []
                for related in cwe_item.get("related_weaknesses", []):
                    cwe_ref_id = related.get("cwe_id", "")
                    if cwe_ref_id and not cwe_ref_id.startswith("CWE-"):
                        cwe_ref_id = f"CWE-{cwe_ref_id}"
                    if cwe_ref_id:
                        related_weaknesses.append(cwe_ref_id)

                try:
                    cwe_record, created = await CWE.get_or_create(
                        cwe_id=cwe_id,
                        defaults={
                            "name": name,
                            "description": description,
                            "category": category,
                            "related_weaknesses": related_weaknesses,
                            "mitre_data": cwe_item,
                        },
                    )
                    if created:
                        total_created += 1
                    total_synced += 1

                    if max_results and total_synced >= max_results:
                        logger.info(f"Reached max_results limit ({max_results})")
                        break

                except Exception as e:
                    logger.error(f"Failed to insert CWE {cwe_id}: {e}")

    except Exception as e:
        logger.error(f"CWE seeding failed: {e}")
        return (0, 0)

    logger.info(f"CWE seed complete: created={total_created}, total={total_synced}")
    return (total_created, total_synced)

