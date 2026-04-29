"""manage package — async CLI dispatcher for CyberSecSuite."""
from logger import getLogger  # noqa: F401

import asyncio
import sys

from ._commands import (
    schema_command,
    init_db_command,
    shell_command,
    status_command,
    seed_all_command,
    seed_command,
    seed_nist_csf_command,
    seed_nist_ai_rmf_command,
    seed_nist_all_command,
    seed_intel_command,
    seed_mitre_command,
    seed_mitre_fixtures_command,
    seed_mitre_actors_command,
    seed_mitre_software_command,
    seed_cwe_command,
    seed_capec_command,
    seed_nvd_cves_command,
    seed_poc_command,
    dashboard_command,
    machine_command,
    case_open_command,
    team_task_command,
    ssl_command,
    vault_command,
    check_command,
    migrate_audit_command,
    migrate_api_usage_command,
    migrate_llm_calls_command,
    migrate_intel_update_log_command,
    build_skill_index_command,
    install_command,
    seed_marketplace_command,
)


def show_usage():
    print("CyberSec Management")
    print("Available commands:")
    print("  schema     - Create / update all tables (generate_schemas safe=True)")
    print("  init-db    - One-shot setup: schema + seed all fixtures (use in entrypoint)")
    print("  shell      - Launch async Python shell with models")
    print("  status     - Show database status")
    print("  seed       - Seed ALL intel tables (NIST + MITRE + CWE + CAPEC)")
    print("  seed-all   - Seed all fixture-based tables (NIST CSF + AI RMF + MITRE + CWE + CAPEC + PoC)")
    print("  seed-intel          - Seed MITRE techniques, actors, software, CWE, CAPEC")
    print("  seed-nist-csf       - Seed NIST CSF 2.0 controls (185 subcategories)")
    print("  seed-nist-ai-rmf    - Seed NIST AI RMF 1.0 controls (72 subcategories)")
    print("  seed-nist-all       - Seed both NIST CSF 2.0 and AI RMF 1.0")
    print("  seed-mitre          - Seed MITRE ATT&CK (live data: techniques + actors + software)")
    print("  seed-mitre-fixtures - Seed MITRE ATT&CK techniques (30 canonical fixture entries)")
    print("  seed-mitre-actors   - Seed MITRE ATT&CK threat actors (12 entries)")
    print("  seed-mitre-software - Seed MITRE ATT&CK software families (14 entries)")
    print("  seed-cwe            - Seed CWE weaknesses (full database)")
    print("  seed-capec          - Seed CAPEC attack patterns (full database)")
    print("  seed-nvd-cves       - Seed CVEs from NVD API v2 (uses httpx, 2000/page)")
    print("                        WARNING: All CVEs takes 30+ min without API key")
    print("                        Flags: --api-key KEY  --max N  --start-year YYYY")
    print("                               --severity CRITICAL|HIGH|MEDIUM|LOW  --incremental")
    print("  seed-poc            - Seed PoC exploit records (5 entries)")
    print("  machine    - Seed / display local machine hardware inventory")
    print("  dashboard  - Generate static HTML dashboard (skills/dashboard/index.html)")
    print("               Flags: --open (open browser)  --serve (live HTTP server)  --port N")
    print("  case-open  - Open a new investigation case (Phase 0 — interactive intake)")
    print("  team-task  - Dispatch task to blue/red/purple team")
    print('               Flags: --team blue|red|purple  --task "desc"  --agents a,b  --mode blue|red|purple')
    print()
    print("SSL / Key Management:")
    print("  ssl create-ca   - Create CA keypair (Ed25519, password-protected)")
    print("                    Flags: --name NAME --pass PASS.txt [--vault-pass VAULT.txt] [--overwrite]")
    print("  ssl create-key  - Create Ed25519 keypair (standalone or under CA)")
    print("                    Flags: --name NAME --pass PASS.txt [--ca CA_NAME] [--overwrite]")
    print("  ssl create-csr  - Generate Certificate Signing Request")
    print("                    Flags: --name NAME --pass PASS.txt --cn CN [--org ORG] [--country CC]")
    print("  ssl list        - List all managed keys and metadata")
    print()
    print("Vault (encrypted secret storage):")
    print("  vault store     - Encrypt and store a secret")
    print("                    Flags: --name NAME --file FILE --master-pass MASTER.txt")
    print("  vault get       - Decrypt and print a secret")
    print("                    Flags: --name NAME --master-pass MASTER.txt")
    print("  vault list      - List all secrets in the vault")
    print("  vault delete    - Remove a secret from the vault")
    print("                    Flags: --name NAME")
    print()
    print("Integrity:")
    print("  check    - Run model, fixture, and config consistency checks")
    print("             Validates FK targets, table names, related_names,")
    print("             fixture coverage, and config cross-references")
    print()
    print("OpenObserve Migrations (fast-forward PG → OO, then drop PG table):")
    print("  migrate-audit            - Copy audit_logs → OO stream 'audit'")
    print("  migrate-api-usage        - Copy api_usage_log → OO stream 'api-usage'")
    print("  migrate-llm-calls        - Copy llm_calls → OO stream 'llm-calls'")
    print("  migrate-intel-update-log - Copy intel_update_log_entries → OO stream 'intel-update-log'")
    print("  build-skill-index - Build merged skill index JSON for global/app/project scopes")
    print()
    print("App install:")
    print("  install  - Create ~/.cybersecsuite/ directory structure (idempotent)")
    print("             Set CYBERSECSUITE_HOME to override the default path")
    print("  seed-marketplace - Seed marketplace from bundled search-index.json (1064 entries)")
    print("                     Safe to re-run (idempotent: skips existing entries)")


async def main():
    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1]

    async_commands = {
        "schema": schema_command,
        "init-db": init_db_command,
        "shell": shell_command,
        "status": status_command,
        "seed": seed_command,
        "seed-all": seed_all_command,
        "seed-intel": seed_intel_command,
        "seed-nist-csf": seed_nist_csf_command,
        "seed-nist-ai-rmf": seed_nist_ai_rmf_command,
        "seed-nist-all": seed_nist_all_command,
        "seed-mitre": seed_mitre_command,
        "seed-mitre-fixtures": seed_mitre_fixtures_command,
        "seed-mitre-actors": seed_mitre_actors_command,
        "seed-mitre-software": seed_mitre_software_command,
        "seed-cwe": seed_cwe_command,
        "seed-capec": seed_capec_command,
        "seed-nvd-cves": seed_nvd_cves_command,
        "seed-poc": seed_poc_command,
        "machine": machine_command,
        "case-open": case_open_command,
        "team-task": team_task_command,
        "migrate-audit": migrate_audit_command,
        "migrate-api-usage": migrate_api_usage_command,
        "migrate-llm-calls": migrate_llm_calls_command,
        "migrate-intel-update-log": migrate_intel_update_log_command,
        "build-skill-index": build_skill_index_command,
        "install": install_command,
        "seed-marketplace": seed_marketplace_command,
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

    if len(sys.argv) >= 2 and sys.argv[1] == "ssl":
        ssl_command()
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] == "vault":
        vault_command()
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] == "check":
        check_command()
        sys.exit(0)

    try:
        from hooks.uvloop_integration import run_with_uvloop

        run_with_uvloop(main())
    except ImportError:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)


def main_sync() -> None:
    """Synchronous entry point for `cybersecsuite` installed script."""
    _run_main()
