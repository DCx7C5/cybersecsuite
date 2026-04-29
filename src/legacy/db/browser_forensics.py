"""
Browser forensics data access — ORM wrapper for browser forensic findings.
Replaces raw sqlite3 calls in browser-hunt command.
"""
from datetime import datetime, timezone
from typing import Any

from tortoise.functions import Count

from db.models import BrowserForensicFinding


async def log_finding_async(
    severity: str,
    title: str,
    description: str,
    source: str = "browser-hunt",
    evidence: list[str] | None = None,
    browser: str = "",
) -> BrowserForensicFinding:
    """
    Log a browser forensic finding to the database.

    Args:
        severity: One of "critical", "high", "medium", "low"
        title: Finding title
        description: Finding description
        source: Source (default: "browser-hunt")
        evidence: List of evidence items
        browser: Browser name (brave, chrome, firefox)

    Returns:
        Created BrowserForensicFinding instance
    """
    finding = await BrowserForensicFinding.create(
        severity=severity,
        title=title,
        description=description,
        source=source,
        evidence=evidence or [],
        browser=browser,
        timestamp=datetime.now(timezone.utc),
    )
    return finding


async def list_findings_by_browser(browser: str) -> list[BrowserForensicFinding]:
    """Get all findings for a specific browser."""
    return await BrowserForensicFinding.filter(browser=browser).order_by("-timestamp")


async def list_findings_by_severity(severity: str) -> list[BrowserForensicFinding]:
    """Get all findings with a specific severity level."""
    return await BrowserForensicFinding.filter(severity=severity).order_by("-timestamp")


async def count_findings_by_severity() -> dict[str, int]:
    """Get finding count aggregated by severity."""
    results = await (
        BrowserForensicFinding.all()
        .group_by("severity")
        .annotate(count=Count("id"))
        .values("severity", "count")
    )
    return {r["severity"]: r["count"] for r in results}


async def get_top_suspicious_domains(browser: str, limit: int = 20) -> list[dict[str, Any]]:
    """
    Get top domains with suspicious activity (from findings).

    This is a computed view from the findings table;
    actual browser DB is accessed via sqlite3 in analyze_cookies.
    """
    findings = await BrowserForensicFinding.filter(
        browser=browser,
        title__icontains="Cookie",
    ).limit(limit)
    return [
        {
            "title": f.title,
            "description": f.description,
            "severity": f.severity,
        }
        for f in findings
    ]


async def get_suspicious_downloads(browser: str) -> list[BrowserForensicFinding]:
    """Get all suspicious download findings for a browser."""
    return await BrowserForensicFinding.filter(
        browser=browser,
        title__icontains="Download",
    ).order_by("-timestamp")


async def delete_findings_for_browser(browser: str) -> int:
    """Clean up old findings for a browser. Returns count deleted."""
    return await BrowserForensicFinding.filter(browser=browser).delete()

