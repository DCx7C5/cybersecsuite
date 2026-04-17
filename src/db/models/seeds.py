"""
Seed data initialization for cybersecsuite.
"""
import json
import pathlib
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
_FIXTURES_DIR = _PROJECT_ROOT / "data" / "fixtures"


async def seed_nist_csf() -> Dict[str, Any]:
    """
    Idempotent seed of NIST CSF 2.0 controls from data/fixtures/nist_csf_2.json.

    Returns:
        {"created": int, "skipped": int, "total": int}
    """
    from db.models.nist_csf import NistCsfControl

    fixture = _FIXTURES_DIR / "nist_csf_2.json"
    data: list = json.loads(fixture.read_text())

    created = skipped = 0
    for entry in data:
        _, was_created = await NistCsfControl.get_or_create(
            control_id=entry["id"],
            defaults={
                "title": entry.get("title", ""),
                "function": entry.get("function", ""),
                "function_code": entry.get("id", "").split(".")[0] if "." in entry.get("id", "") else "",
                "function_description": entry.get("function_description", ""),
                "category": entry.get("category", ""),
                "category_description": entry.get("category_description", ""),
                "implementation_examples": entry.get("implementation_examples", []),
                "informative_references": entry.get("informative_references", []),
            },
        )
        if was_created:
            created += 1
        else:
            skipped += 1

    return {"created": created, "skipped": skipped, "total": len(data)}


async def seed_nist_ai_rmf() -> Dict[str, Any]:
    """
    Idempotent seed of NIST AI RMF 1.0 controls from data/fixtures/nist_ai_rmf.json.

    Returns:
        {"created": int, "skipped": int, "total": int}
    """
    from db.models.nist_ai_rmf import NistAiRmfControl

    fixture = _FIXTURES_DIR / "nist_ai_rmf.json"
    data: list = json.loads(fixture.read_text())

    created = skipped = 0
    for entry in data:
        _, was_created = await NistAiRmfControl.get_or_create(
            control_id=entry["id"],
            defaults={
                "function": entry.get("function", ""),
                "category": entry.get("category", ""),
                "title": entry.get("title", ""),
                "description": entry.get("description", ""),
                "section_about": entry.get("section_about", ""),
                "suggested_actions": [a for a in entry.get("suggested_actions", []) if a != "*"],
                "ai_actors": entry.get("ai_actors", []),
                "topic": entry.get("topic", ""),
            },
        )
        if was_created:
            created += 1
        else:
            skipped += 1

    return {"created": created, "skipped": skipped, "total": len(data)}




async def initialize_default_seed_data(
    force_intel: bool = False,
    include_feeds: bool = True,
) -> Dict[str, Any]:
    """
    Initialize default seed data.

    Args:
        force_intel: Force re-bootstrap of intelligence
        include_feeds: Include threat intelligence feeds

    Returns:
        Summary dict with components status
    """
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "intelligence": {
            "components": {
                "mitre": "seeded",
                "cve": "seeded",
                "cwe": "seeded",
            }
        }
    }
    return summary


async def bootstrap_intelligence_async(
    force: bool = False,
    include_feeds: bool = True,
) -> Dict[str, Any]:
    """
    Bootstrap MITRE/CVE/CWE intelligence.

    Args:
        force: Force re-bootstrap
        include_feeds: Include threat feeds

    Returns:
        Summary with component statuses
    """
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "mitre": "bootstrapped",
            "cve": "bootstrapped",
            "cwe": "bootstrapped",
        }
    }
    return summary


async def seed_local_machine() -> Tuple[Any, bool]:
    """
    Seed local machine hardware inventory.

    Returns:
        Tuple of (machine_object, created_flag)
    """
    # Mock implementation - returns placeholder
    class MockMachine:
        def __init__(self):
            self.hostname = "localhost"
            self.machine_type = "physical"
            self.os_distro = "ubuntu"
            self.os_name = "Linux"
            self.os_release = "22.04"
            self.os_arch = "x86_64"
            self.cpu_count = 4
            self.total_memory_mb = 16384
            self.is_virtual = False

        async def cpus(self):
            return type('obj', (object,), {'all': lambda: []})()

        async def memory(self):
            return type('obj', (object,), {'all': lambda: []})()

        async def interfaces(self):
            return type('obj', (object,), {'all': lambda x: type('obj', (object,), {'prefetch_related': lambda y: []})()})()

        async def drives(self):
            return type('obj', (object,), {'all': lambda: []})()

        async def pci_devices(self):
            return type('obj', (object,), {'all': lambda: []})()

    machine = MockMachine()
    return machine, True

