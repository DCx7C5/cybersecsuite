#!/usr/bin/env python3
"""
CyberSec Tortoise ORM Management Script.

Schema is managed directly via generate_schemas(safe=True) — no migrations.
"""
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def show_usage():
    print("CyberSec Management")
    print("Available commands:")
    print("  schema     - Create / update all tables (generate_schemas safe=True)")
    print("  shell      - Launch async Python shell with models")
    print("  status     - Show database status")
    print("  seed       - Seed ALL intel tables (NIST + MITRE + CWE + CAPEC)")
    print("  seed-intel          - Seed MITRE techniques, actors, software, CWE, CAPEC")
    print("  seed-nist-csf       - Seed NIST CSF 2.0 controls (185 subcategories)")
    print("  seed-nist-ai-rmf    - Seed NIST AI RMF 1.0 controls (72 subcategories)")
    print("  seed-nist-all       - Seed both NIST CSF 2.0 and AI RMF 1.0")
    print("  seed-mitre          - Seed MITRE ATT&CK techniques (30 entries)")
    print("  seed-mitre-actors   - Seed MITRE ATT&CK threat actors (12 entries)")
    print("  seed-mitre-software - Seed MITRE ATT&CK software families (14 entries)")
    print("  seed-cwe            - Seed CWE weaknesses (18 entries)")
    print("  seed-capec          - Seed CAPEC attack patterns (20 entries)")
    print("  machine    - Seed / display local machine hardware inventory")
    print("  dashboard  - Generate static HTML dashboard (skills/dashboard/index.html)")
    print("               Flags: --open (open browser)  --serve (live HTTP server)  --port N")
    print("  case-open  - Open a new investigation case (Phase 0 — interactive intake)")
    print("  ssl-genkey - Generate SSL/TLS certificate for proxy (port 8433)")
    print("  ssl-info   - Display SSL/TLS certificate information")
    print("  ssl-verify - Verify SSL/TLS certificate validity")


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
        **{name: getattr(models, name) for name in ("Workspace", "Project", "Session", "Finding", "IOC")},
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
    print(f"Tables ({health.get('table_count', 0)}): {', '.join(health.get('tables', [])) or '(none)'}")
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
                sub_status = sub_summary.get("status", "?") if isinstance(sub_summary, dict) else "?"
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
    print(f"✅ NIST CSF 2.0: {result['created']} created, {result['skipped']} skipped ({result['total']} total)")


async def seed_nist_ai_rmf_command():
    """Seed NIST AI RMF 1.0 controls (72 subcategories)."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_nist_ai_rmf

    await init_tortoise_async(create_db=True)
    print("→ Seeding NIST AI RMF 1.0 controls...")
    result = await seed_nist_ai_rmf()
    print(f"✅ NIST AI RMF 1.0: {result['created']} created, {result['skipped']} skipped ({result['total']} total)")


async def seed_nist_all_command():
    """Seed both NIST CSF 2.0 and AI RMF 1.0."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_nist_csf, seed_nist_ai_rmf

    await init_tortoise_async(create_db=True)
    print("→ Seeding NIST CSF 2.0 controls...")
    csf = await seed_nist_csf()
    print(f"✅ NIST CSF 2.0: {csf['created']} created, {csf['skipped']} skipped ({csf['total']} total)")
    print("→ Seeding NIST AI RMF 1.0 controls...")
    rmf = await seed_nist_ai_rmf()
    print(f"✅ NIST AI RMF 1.0: {rmf['created']} created, {rmf['skipped']} skipped ({rmf['total']} total)")


async def seed_intel_command():
    """Bootstrap all MITRE/CWE/CAPEC intel tables from curated fixture files."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import (
        seed_mitre_techniques, seed_mitre_actors, seed_mitre_software,
        seed_cwe, seed_capec,
    )

    await init_tortoise_async(create_db=True)
    for label, fn in [
        ("MITRE Techniques", seed_mitre_techniques),
        ("MITRE Actors",     seed_mitre_actors),
        ("MITRE Software",   seed_mitre_software),
        ("CWE",              seed_cwe),
        ("CAPEC",            seed_capec),
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
    print(f"✅ MITRE Techniques: {r['created']} created, {r['skipped']} skipped ({r['total']} total)")


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
    """Seed CWE weakness entries (18 canonical entries)."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_cwe
    await init_tortoise_async(create_db=True)
    r = await seed_cwe()
    print(f"✅ CWE: {r['created']} created, {r['skipped']} skipped ({r['total']} total)")


async def seed_capec_command():
    """Seed CAPEC attack pattern entries (20 canonical entries)."""
    from db.bootstrap import init_tortoise_async
    from db.models.seeds import seed_capec
    await init_tortoise_async(create_db=True)
    r = await seed_capec()
    print(f"✅ CAPEC: {r['created']} created, {r['skipped']} skipped ({r['total']} total)")


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
            print(f"     [{cpu.socket_id}] {cpu.model_name}  "
                  f"{cpu.cores}C/{cpu.threads}T  {cpu.base_freq_mhz or '?'} MHz")

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
            print(f"     {nic.name:<12} {nic.mac_address or '—':18} "
                  f"{'UP' if nic.is_up else 'DOWN':4}  {', '.join(addrs) or '—'}")

    drive_rows = await machine.drives.all()
    if drive_rows:
        print(f"   Drives : {len(drive_rows)}")
        for d in drive_rows:
            gb = d.capacity_bytes // (1024 ** 3) if d.capacity_bytes else 0
            print(f"     {d.device_path:<16} {d.drive_type:5}  {gb:>6} GB  {d.model_name or '—'}")

    pci_rows = await machine.pci_devices.all()
    if pci_rows:
        print(f"   PCI    : {len(pci_rows)} device(s)")


async def case_open_command():
    """Open a new investigation case interactively (Phase 0)."""
    from db.bootstrap import init_tortoise_async
    from db.models.case_intake import CaseIntake
    from db.models.scope import Workspace
    from db.models.enums import Severity, RedBlueMode

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

    priority_input = input("Priority (low/medium/high/critical) [medium]: ").strip().lower() or "medium"
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


async def main():
    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1]

    async_commands = {
        "schema":           schema_command,
        "shell":            shell_command,
        "status":           status_command,
        "seed":                 seed_command,
        "seed-intel":           seed_intel_command,
        "seed-nist-csf":        seed_nist_csf_command,
        "seed-nist-ai-rmf":     seed_nist_ai_rmf_command,
        "seed-nist-all":        seed_nist_all_command,
        "seed-mitre":           seed_mitre_command,
        "seed-mitre-actors":    seed_mitre_actors_command,
        "seed-mitre-software":  seed_mitre_software_command,
        "seed-cwe":             seed_cwe_command,
        "seed-capec":           seed_capec_command,
        "machine":          machine_command,
        "case-open":        case_open_command,
    }

    if command not in async_commands:
        print(f"Unknown command: {command}")
        show_usage()
        sys.exit(1)

    await async_commands[command]()


def _run_main() -> None:
    """Shared entry point for both __main__ and installed script."""
    if len(sys.argv) >= 2 and sys.argv[1] == "dashboard":
        dashboard_command()
        sys.exit(0)

    try:
        from hooks.uvloop_integration import run_with_uvloop
        run_with_uvloop(main())
    except ImportError:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)


if __name__ == "__main__":
    _run_main()


def main_sync() -> None:
    """Synchronous entry point for `cybersecsuite` installed script."""
    _run_main()

