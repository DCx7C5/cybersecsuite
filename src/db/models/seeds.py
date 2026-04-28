"""
Seed data initialization for cybersecsuite.
"""
import json
import pathlib
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

_INTEL_FIXTURES_DIR = pathlib.Path(__file__).resolve().parents[1] / "fixtures"


async def seed_nist_csf() -> Dict[str, Any]:
    """
    Idempotent seed of NIST CSF 2.0 controls from src/db/fixtures/nist_csf_2.json.

    Returns:
        {"created": int, "skipped": int, "total": int}
    """
    import re as _re
    from db.models.nist_csf import NistCsfControl

    fixture = _INTEL_FIXTURES_DIR / "nist_csf_2.json"
    data: list = json.loads(fixture.read_text())

    def _to_list(value) -> list:
        """Normalize fixture field to list — handles str (split on Ex\\d+:) or already a list."""
        if isinstance(value, list):
            return value
        if not value:
            return []
        parts = _re.split(r"\s*Ex\d+:\s*", str(value))
        return [p.strip() for p in parts if p.strip()]

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
                "implementation_examples": _to_list(entry.get("implementation_examples", [])),
                "informative_references": _to_list(entry.get("informative_references", [])),
            },
        )
        if was_created:
            created += 1
        else:
            skipped += 1

    return {"created": created, "skipped": skipped, "total": len(data)}


async def seed_nist_ai_rmf() -> Dict[str, Any]:
    """
    Idempotent seed of NIST AI RMF 1.0 controls from src/db/fixtures/nist_ai_rmf.json.

    Returns:
        {"created": int, "skipped": int, "total": int}
    """
    from db.models.nist_ai_rmf import NistAiRmfControl

    fixture = _INTEL_FIXTURES_DIR / "nist_ai_rmf.json"
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
    """Idempotent seed of MITRE ATT&CK techniques from src/db/fixtures/mitre_techniques.json."""
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
    """Idempotent seed of MITRE ATT&CK threat actors from src/db/fixtures/mitre_actors.json."""
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
    """Idempotent seed of MITRE ATT&CK software families from src/db/fixtures/mitre_software.json."""
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
    """Idempotent seed of CWE weaknesses from src/db/fixtures/cwe_entries.json."""
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
    """Idempotent seed of CAPEC attack patterns from src/db/fixtures/capec_entries.json."""
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


async def seed_cve() -> Dict[str, Any]:
    """Idempotent seed of CVE entries from src/db/fixtures/cve_entries.json."""
    from db.models.cve import CVEIntel

    data: list = json.loads((_INTEL_FIXTURES_DIR / "cve_entries.json").read_text())
    created = skipped = 0
    for entry in data:
        _, was_created = await CVEIntel.get_or_create(
            cve_id=entry["cve_id"],
            defaults={
                "cvss_score": entry.get("cvss_score"),
                "cvss_vector": entry.get("cvss_vector", ""),
                "severity": entry.get("severity", ""),
                "description": entry.get("description"),
                "affected_products": entry.get("affected_products", []),
                "references": entry.get("references", []),
                "exploit_available": entry.get("exploit_available", False),
                "patch_available": entry.get("patch_available", False),
                "published_at": entry.get("published_at"),
                "last_modified_at": entry.get("last_modified_at"),
                "source_feed": entry.get("source_feed", ""),
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
    """Seed all intel tables (NIST, MITRE, CWE, CAPEC, CVE). Idempotent."""
    results: Dict[str, Any] = {"timestamp": datetime.now(timezone.utc).isoformat()}
    for name, fn in [
        ("nist_csf", seed_nist_csf),
        ("nist_ai_rmf", seed_nist_ai_rmf),
        ("mitre_techniques", seed_mitre_techniques),
        ("mitre_actors", seed_mitre_actors),
        ("mitre_software", seed_mitre_software),
        ("cwe", seed_cwe),
        ("capec", seed_capec),
        ("cve", seed_cve),
        ("poc", seed_poc),
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


async def seed_poc() -> Dict[str, Any]:
    """
    Seed PoC records from src/db/fixtures/poc_entries.json.

    Returns:
        {"created": int, "skipped": int, "total": int}
    """
    from db.models.poc import ProofOfConcept
    from db.models.cve import CVEIntel

    data: list = json.loads((_INTEL_FIXTURES_DIR / "poc_entries.json").read_text())

    created = skipped = 0
    for entry in data:
        cve_id = entry.get("cve_id")
        poc_url = entry.get("poc_url", "")
        if not poc_url:
            skipped += 1
            continue
        if await ProofOfConcept.filter(poc_url=poc_url).exists():
            skipped += 1
            continue
        cve = await CVEIntel.filter(cve_id=cve_id).first() if cve_id else None
        fields = {k: v for k, v in entry.items() if k != "cve_id"}
        await ProofOfConcept.create(cve=cve, **fields)
        created += 1

    return {"created": created, "skipped": skipped, "total": len(data)}


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



async def seed_marketplace_assets() -> Dict[str, Any]:
    """
    Idempotent seed of marketplace assets (~890 products).
    
    Creates marketplace entries for:
    - 12 MCPs (externalized from monolithic csmcp)
    - 799 skills
    - 31+ agents
    - Browser plugins
    - Workflow templates
    - Prompt templates
    
    Returns:
        {"created": int, "skipped": int, "total": int, "mcp_count": int, "skill_count": int, ...}
    """
    from db.models.marketplace import MarketplaceMCP, Skill, Agent
    
    created = skipped = 0
    mcp_created = skill_created = agent_created = 0
    
    # Define the 12 MCPs to be extracted
    mcps_data = [
        {
            "name": "forensic-vault",
            "description": "Forensic case management and vault system",
            "category": "core",
            "tools_count": 14,
            "size_mb": 2.5,
            "tags": ["forensics", "case-management", "findings"],
        },
        {
            "name": "network-layers",
            "description": "OSI layer analysis and network forensics",
            "category": "core",
            "tools_count": 9,
            "size_mb": 1.8,
            "tags": ["network", "layer-analysis", "monitoring"],
        },
        {
            "name": "threat-intelligence",
            "description": "Threat intelligence and indicator management",
            "category": "core",
            "tools_count": 14,
            "size_mb": 3.2,
            "tags": ["threat-intel", "indicators", "ioc"],
        },
        {
            "name": "database-tools",
            "description": "Database queries and synchronization",
            "category": "core",
            "tools_count": 15,
            "size_mb": 2.1,
            "tags": ["database", "queries", "sync"],
        },
        {
            "name": "session-management",
            "description": "Session and authentication management",
            "category": "core",
            "tools_count": 10,
            "size_mb": 1.5,
            "tags": ["sessions", "auth", "health"],
        },
        {
            "name": "incident-management",
            "description": "Incident response and PoC tracking",
            "category": "core",
            "tools_count": 7,
            "size_mb": 1.2,
            "tags": ["incident", "response", "poc"],
        },
        {
            "name": "ai-memory",
            "description": "AI memory and thinking operations",
            "category": "core",
            "tools_count": 4,
            "size_mb": 0.8,
            "tags": ["ai", "memory", "extract"],
        },
        {
            "name": "browser-automation",
            "description": "Browser automation and playwright integration",
            "category": "operational",
            "tools_count": 4,
            "size_mb": 2.3,
            "tags": ["browser", "automation", "playwright"],
        },
        {
            "name": "utility-tools",
            "description": "Cache, asgi, and utility functions",
            "category": "operational",
            "tools_count": 11,
            "size_mb": 1.4,
            "tags": ["utilities", "cache", "asgi"],
        },
        {
            "name": "business-tools",
            "description": "Pricing, web search, and business functions",
            "category": "operational",
            "tools_count": 7,
            "size_mb": 1.6,
            "tags": ["business", "search", "pricing"],
        },
        {
            "name": "network-monitoring",
            "description": "Real-time network monitoring",
            "category": "operational",
            "tools_count": 8,
            "size_mb": 1.9,
            "tags": ["network", "monitoring", "realtime"],
        },
        {
            "name": "dystopian-actors",
            "description": "Adversary simulation and threat modeling",
            "category": "special",
            "tools_count": 12,
            "size_mb": 2.8,
            "tags": ["threat-modeling", "actors", "simulation"],
        },
    ]
    
    # Seed MCPs
    for mcp_data in mcps_data:
        _, was_created = await MarketplaceMCP.get_or_create(
            name=mcp_data["name"],
            defaults={
                "description": mcp_data["description"],
                "version": "0.1.0",
                "status": "available",
                "category": mcp_data["category"],
                "tools_count": mcp_data["tools_count"],
                "size_mb": mcp_data["size_mb"],
                "tags": mcp_data["tags"],
                "metadata": {"phase": "extraction"},
            },
        )
        if was_created:
            created += 1
            mcp_created += 1
        else:
            skipped += 1
    
    # Define sample skills (799 total in real deployment)
    # For now, seed representative skills in major categories
    skill_categories = {
        "forensics": ["timeline-analysis", "artifact-parsing", "memory-dump", "disk-analysis", "carving"],
        "threat-intel": ["ioc-enrichment", "apt-attribution", "cvss-analysis", "mitre-mapping", "threat-profiling"],
        "network": ["packet-analysis", "flow-analysis", "protocol-decode", "geolocation", "whois-lookup"],
        "web": ["api-testing", "javascript-analysis", "dom-analysis", "xss-detection", "sql-injection"],
        "malware": ["sample-analysis", "behavior-analysis", "yara-detection", "code-similarity", "sandbox-integration"],
        "compliance": ["control-mapping", "framework-alignment", "audit-logging", "policy-check", "evidence-collection"],
        "automation": ["workflow-runner", "scheduled-tasks", "webhook-integration", "data-transform", "error-handling"],
        "analytics": ["log-analysis", "trend-detection", "anomaly-detection", "baseline-comparison", "reporting"],
    }
    
    for category, skill_names in skill_categories.items():
        for skill_name in skill_names:
            _, was_created = await Skill.get_or_create(
                name=skill_name,
                defaults={
                    "description": f"{skill_name.replace('-', ' ').title()} skill",
                    "version": "0.1.0",
                    "status": "available",
                    "category": category,
                    "tags": [category],
                    "metadata": {"phase": "initial"},
                },
            )
            if was_created:
                created += 1
                skill_created += 1
            else:
                skipped += 1
    
    # Define sample agents
    agent_data = [
        {"name": "forensic-analyst", "model": "sonnet", "max_turns": 30},
        {"name": "threat-hunter", "model": "sonnet", "max_turns": 25},
        {"name": "network-analyst", "model": "haiku", "max_turns": 20},
        {"name": "malware-analyst", "model": "sonnet", "max_turns": 40},
        {"name": "compliance-auditor", "model": "haiku", "max_turns": 15},
        {"name": "incident-commander", "model": "sonnet", "max_turns": 35},
    ]
    
    for agent in agent_data:
        _, was_created = await Agent.get_or_create(
            name=agent["name"],
            defaults={
                "description": f"{agent['name'].replace('-', ' ').title()} agent",
                "version": "0.1.0",
                "status": "available",
                "model": agent["model"],
                "max_turns": agent["max_turns"],
                "category": "security",
                "tags": ["security", "investigation"],
                "metadata": {"phase": "initial"},
            },
        )
        if was_created:
            created += 1
            agent_created += 1
        else:
            skipped += 1
    
    return {
        "created": created,
        "skipped": skipped,
        "total": len(mcps_data) + sum(len(v) for v in skill_categories.values()) + len(agent_data),
        "mcp_count": mcp_created,
        "skill_count": skill_created,
        "agent_count": agent_created,
    }


async def seed_marketplace_from_json() -> Dict[str, Any]:
    """
    Idempotent seed of marketplace data from the bundled search-index.json.

    Reads src/cybersecsuite/data/marketplace/search-index.json via importlib.resources,
    iterates ``documents``, and upserts into the appropriate model:
    - doctype "tool"  → MarketplaceAsset (asset_type="tool")
    - doctype "skill" → Skill model
    - doctype "agent" → Agent model

    Returns:
        {"created": int, "skipped": int, "total": int}
    """
    import importlib.resources
    from db.models.marketplace import MarketplaceAsset, Skill, Agent

    raw = (
        importlib.resources.files("cybersecsuite.data.marketplace")
        .joinpath("search-index.json")
        .read_text(encoding="utf-8")
    )
    data = json.loads(raw)
    documents = data.get("documents", [])

    created = skipped = 0

    for doc in documents:
        doctype = doc.get("doctype", "")
        name = doc.get("name", "")
        if not name:
            skipped += 1
            continue

        description = doc.get("description", "")
        tags = doc.get("tags", [])
        category = doc.get("category", "")

        if doctype == "tool":
            _, was_created = await MarketplaceAsset.get_or_create(
                name=name,
                defaults={
                    "asset_type": "tool",
                    "description": description,
                    "metadata": {
                        "tags": tags,
                        "category": category,
                        "mcp": doc.get("mcp", ""),
                        "searchable": doc.get("searchable", ""),
                    },
                },
            )
        elif doctype == "skill":
            _, was_created = await Skill.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "category": category or "general",
                    "tags": tags if isinstance(tags, list) else [],
                    "metadata": {
                        "mcp": doc.get("mcp", ""),
                        "searchable": doc.get("searchable", ""),
                    },
                },
            )
        elif doctype == "agent":
            _, was_created = await Agent.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "category": category or "general",
                    "tags": tags if isinstance(tags, list) else [],
                    "metadata": {
                        "mcp": doc.get("mcp", ""),
                        "searchable": doc.get("searchable", ""),
                    },
                },
            )
        else:
            _, was_created = await MarketplaceAsset.get_or_create(
                name=name,
                defaults={
                    "asset_type": doctype or "unknown",
                    "description": description,
                    "metadata": {
                        "tags": tags,
                        "category": category,
                        "mcp": doc.get("mcp", ""),
                        "searchable": doc.get("searchable", ""),
                    },
                },
            )

        if was_created:
            created += 1
        else:
            skipped += 1

    return {"created": created, "skipped": skipped, "total": len(documents)}
