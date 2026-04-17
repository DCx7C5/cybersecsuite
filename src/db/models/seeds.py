"""
Seed data initialization for cybersecsuite.
"""
import json
import pathlib
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
_FIXTURES_DIR = _PROJECT_ROOT / "data" / "fixtures"
_INTEL_FIXTURES_DIR = pathlib.Path(__file__).resolve().parents[1] / "fixtures"


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




async def seed_mitre_techniques() -> Dict[str, Any]:
    """Idempotent seed of MITRE ATT&CK techniques from data/fixtures/mitre_techniques.json."""
    from db.models.mitre_technique import MitreTechniqueIntel

    data: list = json.loads((_INTEL_FIXTURES_DIR / "mitre_techniques.json").read_text())
    created = skipped = 0
    for entry in data:
        _, was_created = await MitreTechniqueIntel.get_or_create(
            technique_id=entry["technique_id"],
            defaults={
                "name": entry.get("name", ""),
                "tactics": entry.get("tactics", []),
                "platforms": entry.get("platforms", []),
                "is_sub_technique": entry.get("is_sub_technique", False),
                "parent_technique_id": entry.get("parent_technique_id", ""),
                "description": entry.get("description", ""),
                "detection": entry.get("detection", ""),
                "url": entry.get("url", ""),
                "tags": entry.get("tags", []),
            },
        )
        created += was_created
        skipped += not was_created
    return {"created": created, "skipped": skipped, "total": len(data)}


async def seed_mitre_actors() -> Dict[str, Any]:
    """Idempotent seed of MITRE ATT&CK threat actors from data/fixtures/mitre_actors.json."""
    from db.models.mitre_actor import MitreThreatActorIntel

    data: list = json.loads((_INTEL_FIXTURES_DIR / "mitre_actors.json").read_text())
    created = skipped = 0
    for entry in data:
        _, was_created = await MitreThreatActorIntel.get_or_create(
            actor_name=entry["actor_name"],
            defaults={
                "description": entry.get("description", ""),
                "aliases": entry.get("aliases", []),
                "country_of_origin": entry.get("country_of_origin", ""),
                "motivation": entry.get("motivation", ""),
                "target_sectors": entry.get("target_sectors", []),
                "target_regions": entry.get("target_regions", []),
                "tools_used": entry.get("tools_used", []),
                "url": entry.get("url", ""),
                "tags": entry.get("tags", []),
            },
        )
        created += was_created
        skipped += not was_created
    return {"created": created, "skipped": skipped, "total": len(data)}


async def seed_mitre_software() -> Dict[str, Any]:
    """Idempotent seed of MITRE ATT&CK software families from data/fixtures/mitre_software.json."""
    from db.models.mitre_software import MitreSoftwareFamilyIntel

    data: list = json.loads((_INTEL_FIXTURES_DIR / "mitre_software.json").read_text())
    created = skipped = 0
    for entry in data:
        _, was_created = await MitreSoftwareFamilyIntel.get_or_create(
            software_id=entry["software_id"],
            defaults={
                "name": entry.get("name", ""),
                "software_type": entry.get("software_type", "tool"),
                "description": entry.get("description", ""),
                "aliases": entry.get("aliases", []),
                "platforms": entry.get("platforms", []),
                "is_family": entry.get("is_family", False),
                "url": entry.get("url", ""),
                "tags": entry.get("tags", []),
            },
        )
        created += was_created
        skipped += not was_created
    return {"created": created, "skipped": skipped, "total": len(data)}


async def seed_cwe() -> Dict[str, Any]:
    """Idempotent seed of CWE weaknesses from data/fixtures/cwe_entries.json."""
    from db.models.cwe import CWEIntel

    data: list = json.loads((_INTEL_FIXTURES_DIR / "cwe_entries.json").read_text())
    created = skipped = 0
    for entry in data:
        _, was_created = await CWEIntel.get_or_create(
            cwe_id=entry["cwe_id"],
            defaults={
                "name": entry.get("name", ""),
                "abstraction": entry.get("abstraction", ""),
                "status": entry.get("status", ""),
                "description": entry.get("description", ""),
                "likelihood_of_exploit": entry.get("likelihood_of_exploit", ""),
                "common_consequences": entry.get("common_consequences", []),
                "tags": entry.get("tags", []),
            },
        )
        created += was_created
        skipped += not was_created
    return {"created": created, "skipped": skipped, "total": len(data)}


async def seed_capec() -> Dict[str, Any]:
    """Idempotent seed of CAPEC attack patterns from data/fixtures/capec_entries.json."""
    from db.models.capec import CapecAttackPatternIntel

    data: list = json.loads((_INTEL_FIXTURES_DIR / "capec_entries.json").read_text())
    created = skipped = 0
    for entry in data:
        _, was_created = await CapecAttackPatternIntel.get_or_create(
            capec_id=entry["capec_id"],
            defaults={
                "name": entry.get("name", ""),
                "description": entry.get("description", ""),
                "abstraction": entry.get("abstraction", ""),
                "domains": entry.get("domains", []),
                "likelihood_of_attack": entry.get("likelihood_of_attack", ""),
                "severity": entry.get("severity", ""),
                "url": entry.get("url", ""),
                "tags": entry.get("tags", []),
            },
        )
        created += was_created
        skipped += not was_created
    return {"created": created, "skipped": skipped, "total": len(data)}


async def initialize_default_seed_data(
    force_intel: bool = False,
    include_feeds: bool = True,
) -> Dict[str, Any]:
    """Seed all intel tables (NIST, MITRE, CWE, CAPEC). Idempotent."""
    results: Dict[str, Any] = {"timestamp": datetime.now(timezone.utc).isoformat()}
    for name, fn in [
        ("nist_csf", seed_nist_csf),
        ("nist_ai_rmf", seed_nist_ai_rmf),
        ("mitre_techniques", seed_mitre_techniques),
        ("mitre_actors", seed_mitre_actors),
        ("mitre_software", seed_mitre_software),
        ("cwe", seed_cwe),
        ("capec", seed_capec),
    ]:
        try:
            results[name] = await fn()
        except Exception as exc:
            results[name] = {"error": str(exc)}
    return results


async def bootstrap_intelligence_async(
    force: bool = False,
    include_feeds: bool = True,
) -> Dict[str, Any]:
    """Bootstrap all intelligence tables. Delegates to initialize_default_seed_data."""
    return await initialize_default_seed_data(force_intel=force, include_feeds=include_feeds)


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

