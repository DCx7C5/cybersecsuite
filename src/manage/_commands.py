#!/usr/bin/env python3
"""Command implementations for manage.py."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def schema_command():
    """Create or update all tables using generate_schemas."""
    from db.bootstrap import init_tortoise_async, get_database_health_async

    print("→ Creating/updating schemas...")
    await init_tortoise_async(create_db=True)

    health = await get_database_health_async(check_connection=True, include_counts=False)
    count = health.get("table_count", 0)
    print(f"✅ Done — {count} tables in public schema")


async def shell_command():
    """Launch an interactive shell."""
    from db.bootstrap import init_tortoise_async
    import db.models as models

    await init_tortoise_async()
    print("CyberSec Interactive Shell")
    print("All models imported. Example: await Finding.all()")

    shell_context = {
        "models": models,
        **{
            name: getattr(models, name)
            for name in ("Workspace", "Project", "Session", "Finding", "IOC")
        },
    }

    try:
        import IPython

        IPython.embed(user_ns=shell_context)
    except ImportError:
        import code

        code.interact(local=shell_context)


async def status_command():
    """Show database status."""
    from db.bootstrap import get_database_health_async

    health = await get_database_health_async(check_connection=True, include_counts=True)
    cfg = health.get("config", {})
    host = cfg.get("host", "?")
    port = cfg.get("port")
    conn_str = host if host.startswith("/") else f"{host}:{port}"
    print(f"Initialized : {health['initialized']}")
    print(f"Intel Seeded: {health['intel_bootstrapped']}")
    print(f"DB          : {cfg.get('database', '?')} @ {conn_str}")
    if health.get("status") == "error":
        print(f"Health      : ERROR - {health.get('error')}")
        return
    print(
        f"Tables ({health.get('table_count', 0)}): {', '.join(health.get('tables', [])) or '(none)'}"
    )
    counts = health.get("counts", {})
    if counts:
        print("Intel counts:")
        for key, value in counts.items():
            print(f"  - {key}: {value}")


def _print_intel_components(components: dict) -> None:
    """Print component statuses, handling both flat and nested component dicts."""
    for component, component_summary in components.items():
        if isinstance(component_summary, dict) and "status" in component_summary:
            print(f"   - {component}: {component_summary['status']}")
        elif isinstance(component_summary, dict):
            # Nested sub-components (capec, mitre, misp, opencti)
            for sub_name, sub_summary in component_summary.items():
                sub_status = (
                    sub_summary.get("status", "?") if isinstance(sub_summary, dict) else "?"
                )
                print(f"   - {component}/{sub_name}: {sub_status}")
        else:
            print(f"   - {component}: {component_summary}")


async def seed_command():
    """Seed default data."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import initialize_default_seed_data

    await init_tortoise_async(create_db=True)
    summary = await initialize_default_seed_data(force_intel=False, include_feeds=True)
    for key, val in summary.items():
        if key == "timestamp":
            continue
        if isinstance(val, dict) and "error" not in val:
            print(f"  ✅ {key}: {val.get('created', 0)} created, {val.get('skipped', 0)} skipped")
        elif isinstance(val, dict):
            print(f"  ✗ {key}: {val['error']}")
    print("✅ All intel tables seeded.")


async def seed_nist_csf_command():
    """Seed NIST CSF 2.0 controls (185 subcategories)."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_nist_csf

    await init_tortoise_async(create_db=True)
    print("→ Seeding NIST CSF 2.0 controls...")
    result = await seed_nist_csf()
    print(
        f"✅ NIST CSF 2.0: {result['created']} created, {result['skipped']} skipped ({result['total']} total)"
    )


async def seed_nist_ai_rmf_command():
    """Seed NIST AI RMF 1.0 controls (72 subcategories)."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_nist_ai_rmf

    await init_tortoise_async(create_db=True)
    print("→ Seeding NIST AI RMF 1.0 controls...")
    result = await seed_nist_ai_rmf()
    print(
        f"✅ NIST AI RMF 1.0: {result['created']} created, {result['skipped']} skipped ({result['total']} total)"
    )


async def seed_nist_all_command():
    """Seed both NIST CSF 2.0 and AI RMF 1.0."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_nist_csf, seed_nist_ai_rmf

    await init_tortoise_async(create_db=True)
    print("→ Seeding NIST CSF 2.0 controls...")
    csf = await seed_nist_csf()
    print(
        f"✅ NIST CSF 2.0: {csf['created']} created, {csf['skipped']} skipped ({csf['total']} total)"
    )
    print("→ Seeding NIST AI RMF 1.0 controls...")
    rmf = await seed_nist_ai_rmf()
    print(
        f"✅ NIST AI RMF 1.0: {rmf['created']} created, {rmf['skipped']} skipped ({rmf['total']} total)"
    )


async def seed_intel_command():
    """Bootstrap all MITRE/CWE/CAPEC intel tables from curated fixture files."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import (
        seed_mitre_techniques,
        seed_mitre_actors,
        seed_mitre_software,
        seed_cwe,
        seed_capec,
    )

    await init_tortoise_async(create_db=True)
    for label, fn in [
        ("MITRE Techniques", seed_mitre_techniques),
        ("MITRE Actors", seed_mitre_actors),
        ("MITRE Software", seed_mitre_software),
        ("CWE", seed_cwe),
        ("CAPEC", seed_capec),
    ]:
        print(f"→ Seeding {label}...")
        r = await fn()
        print(f"  ✅ {label}: {r['created']} created, {r['skipped']} skipped ({r['total']} total)")


async def seed_mitre_command():
    """Seed MITRE ATT&CK techniques (30 canonical entries)."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_mitre_techniques

    await init_tortoise_async(create_db=True)
    r = await seed_mitre_techniques()
    print(
        f"✅ MITRE Techniques: {r['created']} created, {r['skipped']} skipped ({r['total']} total)"
    )


async def seed_mitre_actors_command():
    """Seed MITRE ATT&CK threat actors (12 canonical entries)."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_mitre_actors

    await init_tortoise_async(create_db=True)
    r = await seed_mitre_actors()
    print(f"✅ MITRE Actors: {r['created']} created, {r['skipped']} skipped ({r['total']} total)")


async def seed_mitre_software_command():
    """Seed MITRE ATT&CK software families (14 canonical entries)."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_mitre_software

    await init_tortoise_async(create_db=True)
    r = await seed_mitre_software()
    print(f"✅ MITRE Software: {r['created']} created, {r['skipped']} skipped ({r['total']} total)")


async def seed_cwe_command():
    """Seed CWE weakness entries (full database from MITRE)."""
    import argparse
    from db.bootstrap import init_tortoise_async
    from db.seeds.cwe_full import seed_cwe_full

    parser = argparse.ArgumentParser(prog="seed-cwe")
    parser.add_argument("--limit", type=int, default=None, help="Max CWEs to fetch")
    args = parser.parse_args(sys.argv[2:])

    await init_tortoise_async(create_db=True)
    print("⏳ Syncing CWEs from MITRE...")
    created, total = await seed_cwe_full(max_results=args.limit)
    print(f"✅ CWE: {created} created, {total} total synced")


async def seed_capec_command():
    """Seed CAPEC attack pattern entries (full database from MITRE)."""
    import argparse
    from db.bootstrap import init_tortoise_async
    from db.seeds.capec_full import seed_capec_full

    parser = argparse.ArgumentParser(prog="seed-capec")
    parser.add_argument("--limit", type=int, default=None, help="Max CAPECs to fetch")
    args = parser.parse_args(sys.argv[2:])

    await init_tortoise_async(create_db=True)
    print("⏳ Syncing CAPECs from MITRE...")
    created, total = await seed_capec_full(max_results=args.limit)
    print(f"✅ CAPEC: {created} created, {total} total synced")


async def seed_mitre_command():
    """Seed MITRE ATT&CK (techniques + actors + software)."""
    import argparse
    from db.bootstrap import init_tortoise_async
    from db.seeds.mitre_full import seed_mitre_full

    parser = argparse.ArgumentParser(prog="seed-mitre")
    parser.add_argument("--limit", type=int, default=None, help="Max entries per category")
    args = parser.parse_args(sys.argv[2:])

    await init_tortoise_async(create_db=True)
    print("⏳ Syncing MITRE ATT&CK...")
    results = await seed_mitre_full(max_results=args.limit)
    print(f"✅ MITRE ATT&CK synced:")
    print(f"   Techniques: {results['techniques_created']} created, {results['techniques_total']} total")
    print(f"   Actors: {results['actors_created']} created, {results['actors_total']} total")
    print(f"   Software: {results['software_created']} created, {results['software_total']} total")


async def seed_nvd_cves_command():
    """Seed all CVEs from NVD API (National Vulnerability Database).

    Fetches CVEs incrementally from the NVD API and stores in the database.
    This can take a long time (30+ minutes for all CVEs).

    Flags:
      --api-key KEY      NVD API key for higher rate limits (optional)
      --max N            Limit to N CVEs (default: all)
      --start-year YYYY  Only sync CVEs from year YYYY onwards (default: 2010)
      --incremental      Sync only recent CVEs (last 7 days)
    """
    import argparse
    from db.bootstrap import init_tortoise_async
    from db.seeds.nvd import seed_nvd_cves, seed_nvd_cves_incremental

    parser = argparse.ArgumentParser(prog="seed-nvd-cves")
    parser.add_argument("--api-key", default=None, help="NVD API key")
    parser.add_argument("--max", type=int, default=None, help="Max CVEs to fetch")
    parser.add_argument("--start-year", type=int, default=2010, help="Start year for CVEs")
    parser.add_argument("--incremental", action="store_true", help="Sync recent CVEs only")
    args = parser.parse_args(sys.argv[2:])

    await init_tortoise_async(create_db=True)

    print("⏳ Syncing CVEs from NVD...")
    if args.incremental:
        fetched, inserted = await seed_nvd_cves_incremental(api_key=args.api_key)
    else:
        fetched, inserted = await seed_nvd_cves(
            api_key=args.api_key,
            max_results=args.max,
            start_year=args.start_year,
        )
    print(f"✅ NVD CVE Seed complete: fetched={fetched}, inserted={inserted}")


async def seed_poc_command():
    """Seed PoC sample records."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_poc

    await init_tortoise_async(create_db=True)
    result = await seed_poc()
    print(f"✅ PoC seeded: {result['created']} created, {result['skipped']} skipped")


def dashboard_command():
    """Generate a static HTML dashboard (synchronous — has its own arg parser)."""
    import importlib.util

    gen_path = PROJECT_ROOT / "skills" / "dashboard" / "generate_dashboard.py"
    if not gen_path.exists():
        print(f"✗ Dashboard generator not found: {gen_path}", file=sys.stderr)
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("generate_dashboard", gen_path)
    if spec is None or spec.loader is None:
        print(f"✗ Could not load dashboard generator: {gen_path}", file=sys.stderr)
        sys.exit(1)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Forward flags after "dashboard" to the generator's own argparse
    # e.g., python3 manage.py dashboard --serve --port 9000
    sys.argv = [str(gen_path)] + sys.argv[2:]
    mod.main()


async def machine_command():
    """Seed and display local machine hardware inventory."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_local_machine

    await init_tortoise_async(create_db=True)
    machine, created = await seed_local_machine()

    tag = "✅ Created" if created else "ℹ️  Exists"
    print(f"{tag} — {machine.hostname}  [{machine.machine_type}]")
    print(f"   OS     : {machine.os_distro or machine.os_name}  {machine.os_release}")
    print(f"   Arch   : {machine.os_arch}")
    print(f"   CPUs   : {machine.cpu_count} socket(s)   RAM: {machine.total_memory_mb:,} MB")
    print(f"   Virtual: {'yes' if machine.is_virtual else 'no'}")

    cpu_rows = await machine.cpus.all()
    if cpu_rows:
        print("   CPU(s):")
        for cpu in cpu_rows:
            print(
                f"     [{cpu.socket_id}] {cpu.model_name}  "
                f"{cpu.cores}C/{cpu.threads}T  {cpu.base_freq_mhz or '?'} MHz"
            )

    mem_rows = await machine.memory.all()
    if mem_rows:
        total = sum(m.size_mb for m in mem_rows)
        print(f"   Memory : {len(mem_rows)} slot(s)  {total:,} MB total")
        for m in mem_rows:
            print(f"     {m.slot_id or '?'}  {m.size_mb:,} MB  {m.memory_type}  {m.speed_mhz} MHz")

    nic_rows = await machine.interfaces.all().prefetch_related("addresses")
    if nic_rows:
        print(f"   NICs   : {len(nic_rows)}")
        for nic in nic_rows:
            addrs = [a.address for a in nic.addresses]
            print(
                f"     {nic.name:<12} {nic.mac_address or '—':18} "
                f"{'UP' if nic.is_up else 'DOWN':4}  {', '.join(addrs) or '—'}"
            )

    drive_rows = await machine.drives.all()
    if drive_rows:
        print(f"   Drives : {len(drive_rows)}")
        for d in drive_rows:
            gb = d.capacity_bytes // (1024**3) if d.capacity_bytes else 0
            print(f"     {d.device_path:<16} {d.drive_type:5}  {gb:>6} GB  {d.model_name or '—'}")

    pci_rows = await machine.pci_devices.all()
    if pci_rows:
        print(f"   PCI    : {len(pci_rows)} device(s)")


async def case_open_command():
    """Open a new investigation case interactively (Phase 0)."""
    from db.bootstrap import init_tortoise_async
    from db.models.case_intake import CaseIntake
    from db.models.scope import Workspace

    await init_tortoise_async(create_db=True)

    print("═══ Phase 0 — Case Opening ═══\n")

    title = input("Case title: ").strip()
    if not title:
        print("✗ Title is required.")
        return

    problem = input("Problem statement (what happened?): ").strip()
    if not problem:
        print("✗ Problem statement is required.")
        return

    hypothesis = input("Attack hypothesis (optional): ").strip()

    print("\nKnown facts (one per line, empty line to finish):")
    facts: list[str] = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        facts.append(line)

    print("Suspected IOCs (one per line, empty line to finish):")
    iocs: list[str] = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        iocs.append(line)

    print("Affected assets (one per line, empty line to finish):")
    assets: list[str] = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        assets.append(line)

    priority_input = (
        input("Priority (low/medium/high/critical) [medium]: ").strip().lower() or "medium"
    )
    mode_input = input("Mode (blue/red/purple) [blue]: ").strip().lower() or "blue"

    print("MITRE ATT&CK technique IDs (one per line, empty to finish):")
    mitre: list[str] = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        mitre.append(line)

    notes = input("Analyst notes (optional): ").strip()

    ws, _ = await Workspace.get_or_create(name="default")

    intake = await CaseIntake.create(
        workspace=ws,
        title=title,
        problem_statement=problem,
        attack_hypothesis=hypothesis,
        known_facts=facts,
        suspected_iocs=iocs,
        affected_assets=assets,
        priority=priority_input,
        mode=mode_input,
        mitre_hypotheses=mitre,
        analyst_notes=notes,
    )

    print(f"\n✅ Case #{intake.id} opened: {title}")
    print(f"   Priority: {priority_input}  Mode: {mode_input}")
    print(f"   Facts: {len(facts)}  IOCs: {len(iocs)}  Assets: {len(assets)}  MITRE: {len(mitre)}")
    print("   Ready for Phase 1 (Recon).")


async def team_task_command():
    """Create and dispatch an A2A task to a CyberSec team (blue/red/purple)."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="manage.py team-task",
        description="Dispatch a task to a CyberSec agent team.",
    )
    parser.add_argument(
        "--team",
        choices=["blue", "red", "purple"],
        default="blue",
        help="Target team (default: blue)",
    )
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--agents", default="", help="Comma-separated additional agent names")
    parser.add_argument("--mode", default="", help="Override mode (blue/red/purple)")

    args = parser.parse_args(sys.argv[2:])
    team = args.team
    task_desc = args.task
    extra_agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    mode_override = args.mode or team

    team_map = {
        "blue": {
            "agents": [
                "filesystem-analyst",
                "logfile-analyst",
                "memory-analyst",
                "network-analyst",
                "process-analyst",
                "persistence-analyst",
            ],
            "goal": "Defensive forensics: threat hunting, IR, log analysis, hardening",
        },
        "red": {
            "agents": [
                "reverse-engineer",
                "vulnerability-scanner",
                "layer7-specialist",
                "layer4-specialist",
                "layer3-specialist",
            ],
            "goal": "Offensive operations: recon, exploitation, persistence, C2",
        },
        "purple": {
            "agents": [
                "cybersec-analyst",
                "threat-modeler",
                "kernel-analyst",
                "filesystem-analyst",
                "network-analyst",
            ],
            "goal": "Purple team: validate detections, map ATT&CK coverage",
        },
    }

    config = team_map[team]
    agents = config["agents"] + extra_agents

    print(f"🎯 {team.upper()}-TEAM TASK DISPATCH")
    print(f"   Task    : {task_desc}")
    print(f"   Mode    : {mode_override}")
    print(f"   Goal    : {config['goal']}")
    print(f"   Agents  : {', '.join(agents)}")
    print()
    print(f"   Team file: .claude/agents/teams/{team}-team.md")
    print(f'   Execute : claude --agent teams/{team}-team --task "{task_desc}"')


def ssl_command() -> None:
    """Dispatch ``ssl`` sub-commands via Click CLI."""
    from crypto.cli_integration import ssl as ssl_group

    # Re-package argv so Click sees e.g. ["ssl", "create-ca", "--name", ...]
    ssl_group(args=sys.argv[2:], standalone_mode=True)


def vault_command() -> None:
    """Dispatch ``vault`` sub-commands via Click CLI."""
    from crypto.cli_integration import vault as vault_group

    vault_group(args=sys.argv[2:], standalone_mode=True)


def check_command() -> None:
    """Run model, fixture, and config integrity checks."""
    from checks.integrity import run_all_checks

    report = run_all_checks()

    section_labels = {
        "models": "Model Integrity",
        "fixtures": "Fixture Coverage",
        "config": "Config Consistency",
    }

    for section in ("models", "fixtures", "config"):
        findings = report[section]
        label = section_labels[section]
        print(f"\n{'═' * 60}")
        print(f"  {label}")
        print(f"{'═' * 60}")
        if not findings:
            print("  ✅ No issues found")
            continue
        for f in findings:
            level = f["level"]
            if level == "error":
                icon = "✗"
            elif level == "warning":
                icon = "⚠"
            else:
                icon = "✓"
            print(f"  {icon} [{level.upper():7s}] {f['message']}")

    summary = report["summary"]
    print(f"\n{'─' * 60}")
    errors = summary["errors"]
    warnings = summary["warnings"]
    if errors == 0 and warnings == 0:
        print("  ✅ All checks passed — no issues found")
    else:
        parts = []
        if errors:
            parts.append(f"{errors} error(s)")
        if warnings:
            parts.append(f"{warnings} warning(s)")
        status = "✗" if errors else "⚠"
        print(f"  {status} Summary: {', '.join(parts)}")
    print()


# ── OpenSearch fast-forward migrations ───────────────────────────────────────

async def migrate_audit_command() -> None:
    """Fast-forward AuditLog rows from PostgreSQL → OpenSearch, then drop PG table."""
    from db.bootstrap import init_tortoise_async
    from opensearch.client import get_client
    from opensearch.indices import ensure_indices, daily_index

    print("→ Initialising DB...")
    await init_tortoise_async()

    print("→ Ensuring OpenSearch index templates...")
    await ensure_indices()

    from db.models.core import AuditLog
    from tortoise import connections

    total = await AuditLog.all().count()
    print(f"→ Migrating {total} AuditLog rows to OpenSearch...")

    client = get_client()
    batch_size = 500
    migrated = 0
    offset = 0

    while True:
        rows = await AuditLog.all().order_by("id").offset(offset).limit(batch_size)
        if not rows:
            break
        index = daily_index("audit")
        actions: list = []
        for r in rows:
            actions.append({"index": {"_index": index}})
            actions.append({
                "@timestamp": r.created_at.isoformat() if r.created_at else None,
                "action": str(r.action.value) if hasattr(r.action, "value") else str(r.action),
                "entity_type": r.entity_type or "",
                "entity_id": str(r.entity_id) if r.entity_id else None,
                "agent": r.agent or "",
                "resource": r.resource or "",
                "ip_address": r.ip_address or None,
                "detail": r.entity_repr or "",
            })
        await client.bulk(body=actions, refresh=False)
        migrated += len(rows)
        offset += batch_size
        print(f"  {migrated}/{total}...", end="\r")

    print(f"\n✅ Migrated {migrated} rows")

    # Verify count in OpenSearch
    await client.indices.refresh(index=f"cybersecsuite-audit-*")
    resp = await client.count(index=f"cybersecsuite-audit-*")
    os_count = resp.get("count", 0)
    print(f"→ OpenSearch count: {os_count}")

    if os_count < migrated:
        print(f"⚠  Count mismatch ({os_count} < {migrated}) — NOT dropping PG table")
        return

    confirm = input("Drop PG table `audit_logs`? [yes/NO] ").strip().lower()
    if confirm != "yes":
        print("Aborted. PG table NOT dropped.")
        return

    conn = connections.get("default")
    await conn.execute_script("DROP TABLE IF EXISTS audit_logs CASCADE;")
    print("✅ PG table `audit_logs` dropped")


async def migrate_api_usage_command() -> None:
    """Fast-forward ApiUsageLog rows from PostgreSQL → OpenSearch, then drop PG table."""
    from db.bootstrap import init_tortoise_async
    from opensearch.client import get_client
    from opensearch.indices import ensure_indices, daily_index

    print("→ Initialising DB...")
    await init_tortoise_async()

    print("→ Ensuring OpenSearch index templates...")
    await ensure_indices()

    from db.models.api_usage_log import ApiUsageLog
    from tortoise import connections

    total = await ApiUsageLog.all().count()
    print(f"→ Migrating {total} ApiUsageLog rows to OpenSearch...")

    client = get_client()
    batch_size = 500
    migrated = 0
    offset = 0

    while True:
        rows = await ApiUsageLog.all().order_by("timestamp").offset(offset).limit(batch_size)
        if not rows:
            break
        index = daily_index("api-usage")
        actions: list = []
        for r in rows:
            prov = r.provider.value if hasattr(r.provider, "value") else str(r.provider)
            actions.append({"index": {"_index": index}})
            actions.append({
                "@timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "provider": prov,
                "model": r.model or "",
                "tokens_in": r.input_tokens or 0,
                "tokens_out": r.output_tokens or 0,
                "cost_usd": float(r.cost_estimate or 0),
                "duration_ms": None,
                "strategy": None,
            })
        await client.bulk(body=actions, refresh=False)
        migrated += len(rows)
        offset += batch_size
        print(f"  {migrated}/{total}...", end="\r")

    print(f"\n✅ Migrated {migrated} rows")

    await client.indices.refresh(index=f"cybersecsuite-api-usage-*")
    resp = await client.count(index=f"cybersecsuite-api-usage-*")
    os_count = resp.get("count", 0)
    print(f"→ OpenSearch count: {os_count}")

    if os_count < migrated:
        print(f"⚠  Count mismatch ({os_count} < {migrated}) — NOT dropping PG table")
        return

    confirm = input("Drop PG table `api_usage_log`? [yes/NO] ").strip().lower()
    if confirm != "yes":
        print("Aborted. PG table NOT dropped.")
        return

    conn = connections.get("default")
    await conn.execute_script("DROP TABLE IF EXISTS api_usage_log CASCADE;")
    print("✅ PG table `api_usage_log` dropped")

