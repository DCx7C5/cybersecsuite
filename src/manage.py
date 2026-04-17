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


from manage._commands import (
    schema_command,
    shell_command,
    status_command,
    seed_command,
    seed_nist_csf_command,
    seed_nist_ai_rmf_command,
    seed_nist_all_command,
    seed_intel_command,
    seed_mitre_command,
    seed_mitre_actors_command,
    seed_mitre_software_command,
    seed_cwe_command,
    seed_capec_command,
    seed_cve_command,
    seed_poc_command,
    dashboard_command,
    machine_command,
    case_open_command,
    team_task_command,
    ssl_command,
    vault_command,
    check_command,
)

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
    print("  seed-cve            - Seed CVE vulnerability entries (30 entries)")
    print("  seed-poc            - Seed PoC exploit records (5 entries)")
    print("  machine    - Seed / display local machine hardware inventory")
    print("  dashboard  - Generate static HTML dashboard (skills/dashboard/index.html)")
    print("               Flags: --open (open browser)  --serve (live HTTP server)  --port N")
    print("  case-open  - Open a new investigation case (Phase 0 — interactive intake)")
    print("  team-task  - Dispatch task to blue/red/purple team")
    print("               Flags: --team blue|red|purple  --task \"desc\"  --agents a,b  --mode blue|red|purple")
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


async def main():
    if len(sys.argv) < 2:
        show_usage()
        return

    command = sys.argv[1]

    async_commands = {
        "schema":               schema_command,
        "shell":                shell_command,
        "status":               status_command,
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
        "seed-cve":             seed_cve_command,
        "seed-poc":             seed_poc_command,
        "machine":              machine_command,
        "case-open":            case_open_command,
        "team-task":            team_task_command,
    }

    if command not in async_commands:
        print(f"Unknown command: {command}")
        show_usage()
        sys.exit(1)

    await async_commands[command]()


def _run_main() -> None:
    """Shared entry point for both __main__ and installed script."""
    # Synchronous command groups — handled before the async event loop.
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


if __name__ == "__main__":
    _run_main()


def main_sync() -> None:
    """Synchronous entry point for `cybersecsuite` installed script."""
    _run_main()

