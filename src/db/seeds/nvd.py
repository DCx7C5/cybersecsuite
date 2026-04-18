"""
NVD (National Vulnerability Database) CVE seeding — fetches CVEs from NVD API v2.

NVD API v2: https://services.nvd.nist.gov/rest/json/cves/2.0
Rate limit: 5 requests/30 seconds without API key, 50/30s with key.
Max resultsPerPage: 2000.

Supports:
  - --severity CRITICAL|HIGH|MEDIUM|LOW  (filter by CVSS v3 severity)
  - --latest N                           (newest N CVEs by published date)
  - --max N                              (cap total results)
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

from db.models.cve import CVEIntel

logger = logging.getLogger("db.seeds.nvd")

NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_MAX_PER_PAGE = 2000


def _parse_cve(vuln: dict[str, Any]) -> dict[str, Any] | None:
    """Extract fields from a NVD API v2 vulnerability object."""
    cve = vuln.get("cve", {})
    cve_id = cve.get("id", "")
    if not cve_id:
        return None

    # CVSS v3.1 → v3.0 → v2 fallback
    metrics = cve.get("metrics", {})
    cvss_entry = (
        next(iter(metrics.get("cvssMetricV31", [])), None)
        or next(iter(metrics.get("cvssMetricV30", [])), None)
        or next(iter(metrics.get("cvssMetricV2", [])), None)
    )
    cvss_data = (cvss_entry or {}).get("cvssData", {})
    cvss_score: float | None = cvss_data.get("baseScore")
    cvss_vector: str = cvss_data.get("vectorString", "")
    severity: str = (cvss_data.get("baseSeverity") or "unknown").lower()

    # If no baseSeverity, derive from score
    if severity == "unknown" and cvss_score is not None:
        if cvss_score >= 9.0:
            severity = "critical"
        elif cvss_score >= 7.0:
            severity = "high"
        elif cvss_score >= 4.0:
            severity = "medium"
        else:
            severity = "low"

    # Timestamps
    published_str = cve.get("published", "")
    modified_str = cve.get("lastModified", "")

    def _parse_dt(s: str) -> datetime | None:
        if not s:
            return None
        return datetime.fromisoformat(s.replace("Z", "+00:00"))

    published_at = _parse_dt(published_str)
    last_modified_at = _parse_dt(modified_str)

    # English description
    description = next(
        (d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"),
        "",
    )

    # References
    references = [r.get("url", "") for r in cve.get("references", []) if r.get("url")]

    # Weaknesses → CWE IDs in references heuristic
    exploit_available = any(
        "exploit" in (t.lower()) for ref in cve.get("references", []) for t in ref.get("tags", [])
    )
    patch_available = any(
        "patch" in (t.lower()) for ref in cve.get("references", []) for t in ref.get("tags", [])
    )

    return {
        "cve_id": cve_id,
        "cvss_score": cvss_score,
        "cvss_vector": cvss_vector,
        "severity": severity,
        "description": description,
        "references": references,
        "exploit_available": exploit_available,
        "patch_available": patch_available,
        "published_at": published_at,
        "last_modified_at": last_modified_at,
        "source_feed": "NVD",
        "raw_record": vuln,
    }


async def fetch_cve_batch(
    client: httpx.AsyncClient,
    start_index: int = 0,
    results_per_page: int = NVD_MAX_PER_PAGE,
    api_key: str | None = None,
    severity: str | None = None,
    pub_start_date: str | None = None,
    pub_end_date: str | None = None,
) -> dict[str, Any] | None:
    """Fetch one page from NVD API v2. Returns parsed JSON or None on error."""
    params: dict[str, str | int] = {
        "startIndex": start_index,
        "resultsPerPage": results_per_page,
    }
    if severity:
        params["cvssV3Severity"] = severity.upper()
    if pub_start_date:
        params["pubStartDate"] = pub_start_date
    if pub_end_date:
        params["pubEndDate"] = pub_end_date

    headers = {}
    if api_key:
        headers["apiKey"] = api_key

    try:
        resp = await client.get(NVD_API_BASE, params=params, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 429:
            logger.warning("NVD API rate limited (429)")
            return None
        logger.error(f"NVD API error: {resp.status_code}")
        return None
    except httpx.TimeoutException:
        logger.error("NVD API request timeout")
        return None
    except Exception as e:
        logger.error(f"NVD API fetch error: {e}")
        return None


async def seed_nvd_cves(
    api_key: str | None = None,
    max_results: int | None = None,
    start_year: int = 2010,
    severity: str | None = None,
    delay_between_batches: float = 6.5,
) -> tuple[int, int]:
    """
    Seed CVEs from NVD API v2.

    Args:
        api_key: Optional NVD API key (increases rate limit 5×)
        max_results: Cap total CVEs fetched (default: all)
        start_year: Skip CVEs published before this year
        severity: Filter by CVSS v3 severity (CRITICAL/HIGH/MEDIUM/LOW)
        delay_between_batches: Seconds between requests (6.5 no-key, 1.0 with key)

    Returns:
        (total_fetched, total_inserted)
    """
    total_fetched = 0
    total_inserted = 0
    start_index = 0
    failures = 0
    # With API key: 50 req/30s → 0.6s gap; without: 5 req/30s → 6.5s gap
    if api_key:
        delay_between_batches = 0.6

    logger.info(f"Starting NVD CVE seed v2 (start_year={start_year}, severity={severity}, max={max_results})")

    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            data = await fetch_cve_batch(
                client,
                start_index=start_index,
                results_per_page=NVD_MAX_PER_PAGE,
                api_key=api_key,
                severity=severity,
            )

            if not data:
                failures += 1
                if failures >= 3:
                    logger.warning("3 consecutive failures; stopping")
                    break
                await asyncio.sleep(delay_between_batches * 2)
                continue

            failures = 0
            total_results = data.get("totalResults", 0)
            vulns = data.get("vulnerabilities", [])

            if not vulns:
                logger.info(f"No more CVEs at index {start_index}; seed complete")
                break

            logger.info(f"Fetched {len(vulns)} CVEs (index={start_index}/{total_results})")

            for vuln in vulns:
                parsed = _parse_cve(vuln)
                if not parsed:
                    continue

                # Year filter
                if parsed["published_at"] and parsed["published_at"].year < start_year:
                    continue

                try:
                    _, created = await CVEIntel.get_or_create(
                        cve_id=parsed["cve_id"],
                        defaults={k: v for k, v in parsed.items() if k != "cve_id"},
                    )
                    if created:
                        total_inserted += 1
                except Exception as e:
                    logger.error(f"Failed to insert {parsed['cve_id']}: {e}")

                total_fetched += 1
                if max_results and total_fetched >= max_results:
                    logger.info(f"Reached max_results={max_results}")
                    return total_fetched, total_inserted

            start_index += NVD_MAX_PER_PAGE
            if start_index >= total_results:
                break

            await asyncio.sleep(delay_between_batches)

    logger.info(f"NVD seed complete: fetched={total_fetched}, inserted={total_inserted}")
    return total_fetched, total_inserted


async def seed_nvd_cves_incremental(
    days_back: int = 7,
    api_key: str | None = None,
) -> tuple[int, int]:
    """Seed only CVEs modified in the last N days."""
    logger.info(f"Incremental seed: last {days_back} days")
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    pub_start = cutoff.strftime("%Y-%m-%dT%H:%M:%S.000")
    pub_end = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000")

    total_fetched = 0
    total_inserted = 0
    start_index = 0
    timeout = httpx.Timeout(30.0, connect=10.0)
    delay = 0.6 if api_key else 6.5

    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            data = await fetch_cve_batch(
                client,
                start_index=start_index,
                results_per_page=NVD_MAX_PER_PAGE,
                api_key=api_key,
                pub_start_date=pub_start,
                pub_end_date=pub_end,
            )
            if not data:
                break

            vulns = data.get("vulnerabilities", [])
            total_results = data.get("totalResults", 0)
            if not vulns:
                break

            for vuln in vulns:
                parsed = _parse_cve(vuln)
                if not parsed:
                    continue
                try:
                    _, created = await CVEIntel.get_or_create(
                        cve_id=parsed["cve_id"],
                        defaults={k: v for k, v in parsed.items() if k != "cve_id"},
                    )
                    if created:
                        total_inserted += 1
                except Exception as e:
                    logger.error(f"Failed to insert {parsed['cve_id']}: {e}")
                total_fetched += 1

            start_index += NVD_MAX_PER_PAGE
            if start_index >= total_results:
                break
            await asyncio.sleep(delay)

    logger.info(f"Incremental seed complete: fetched={total_fetched}, inserted={total_inserted}")
    return total_fetched, total_inserted

