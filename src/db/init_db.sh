#!/usr/bin/env bash
# DEPRECATED: This script is no longer maintained.
# Use the Python management command instead: uv run python -m manage init-db
# =============================================
# CyberSec — PostgreSQL Database Init Script
# =============================================
# Creates the PostgreSQL database and runs generate_schemas (Tortoise ORM).
# No aerich, no migrations — schema is driven by model definitions.
#
# Usage:
#   ./scripts/init_db.sh                          # defaults
#   CYBERSEC_DB_NAME=mydb ./scripts/init_db.sh    # custom DB name
#   ./scripts/init_db.sh --skip-tests             # skip automated test suite
#   ./scripts/init_db.sh --test-only              # run tests only, no DB changes
#   ./scripts/init_db.sh --skip-seed              # skip seed / intel bootstrap
#   ./scripts/init_db.sh --skip-indexes           # skip performance index creation
#
set -euo pipefail

# --- Argument parsing ---
SKIP_TESTS=0
TEST_ONLY=0
SKIP_SEED=0
SKIP_INDEXES=0

for arg in "$@"; do
  case "$arg" in
    --skip-tests)   SKIP_TESTS=1 ;;
    --test-only)    TEST_ONLY=1 ;;
    --skip-seed)    SKIP_SEED=1 ;;
    --skip-indexes) SKIP_INDEXES=1 ;;
    --help|-h)
      echo "Usage: $0 [--skip-tests] [--test-only] [--skip-seed] [--skip-indexes]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg  (use --help for usage)" >&2
      exit 1
      ;;
  esac
done

DB_NAME="${CYBERSEC_DB_NAME:-cybersec_forensics}"
DB_USER="${CYBERSEC_DB_USER:-cybersec}"
DB_HOST="${CYBERSEC_DB_HOST:-/tmp/.s.PGSQL.}"  # Use socket by default for local connections
DB_PORT="5432"
DB_SUPERUSER="${CYBERSEC_DB_SUPERUSER:-${CYBERSEC_DB_USER:-cybersec}}"
DB_SUPERUSER_PASSWORD="${CYBERSEC_DB_SUPERUSER_PASSWORD:-${CYBERSEC_DB_PASSWORD:-}}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ---- Colour helpers ----
_green()  { printf '\033[0;32m%s\033[0m\n' "$*"; }
_yellow() { printf '\033[1;33m%s\033[0m\n' "$*"; }
_red()    { printf '\033[0;31m%s\033[0m\n' "$*"; }
_blue()   { printf '\033[0;34m%s\033[0m\n' "$*"; }

echo "🔐 CyberSec Comprehensive Forensic Database Init"
echo "   Database: ${DB_NAME} @ ${DB_HOST}:${DB_PORT}"
echo "   User:     ${DB_USER}"
echo "   Superuser:${DB_SUPERUSER}"
echo "   Models:   Comprehensive forensic intelligence framework"
echo "   Flags:    skip-tests=$SKIP_TESTS test-only=$TEST_ONLY skip-seed=$SKIP_SEED skip-indexes=$SKIP_INDEXES"
echo ""

# ==============================================================================
# PHASE 0 — PRE-FLIGHT TESTS (no DB connection required)
# ==============================================================================
run_preflight_tests() {
  _blue "→ [Phase 0] Running pre-flight checks (config + model imports)..."

  export CYBERSEC_DB_HOST="$DB_HOST"
  export CYBERSEC_DB_PORT="$DB_PORT"
  export CYBERSEC_DB_USER="$DB_USER"
  export CYBERSEC_DB_PASSWORD="${CYBERSEC_DB_PASSWORD:-}"
  export CYBERSEC_DB_NAME="$DB_NAME"

  cd "$PROJECT_DIR"
  python3 - <<'PYEOF'
import sys
sys.path.insert(0, ".")

errors = []

# 1. Configuration
try:
    from db.bootstrap import get_database_config, get_tortoise_config
    cfg = get_database_config()
    required = ["host", "port", "user", "database"]
    missing = [k for k in required if not cfg.get(k) and k != "host"]
    if missing:
        errors.append(f"Config missing keys: {missing}")
    else:
        print(f"  ✓ DB config valid: {cfg['database']}@{cfg['host']}:{cfg['port']}")
except Exception as e:
    errors.append(f"Config import failed: {e}")

# 2. Tortoise config
try:
    from db.bootstrap import get_tortoise_config
    tcfg = get_tortoise_config()
    if not tcfg.get("connections"):
        errors.append("Tortoise config has no connections")
    else:
        print(f"  ✓ Tortoise config valid: {list(tcfg['connections'].keys())} connections")
except Exception as e:
    errors.append(f"Tortoise config failed: {e}")

# 3. Model modules
try:
    from db.models import MODEL_MODULES
    if not MODEL_MODULES:
        errors.append("MODEL_MODULES is empty")
    else:
        print(f"  ✓ Models registered: {len(MODEL_MODULES)} modules")
except Exception as e:
    errors.append(f"Model import failed: {e}")

# 4. Core intelligence models
try:
    from db.models.cve import CVEIntel
    from db.models.cwe import CWEIntel
    from db.models.mitre_technique import MitreTechniqueIntel
    from db.models.ioc_entry import IOCDatabaseEntry
    from db.models.feed_snapshot import ThreatIntelFeedSnapshot
    print("  ✓ Core intel models importable")
except Exception as e:
    errors.append(f"Intel model import failed: {e}")

# 5. Bootstrap functions
try:
    from db.intel_loader import (
        bootstrap_intelligence_async,
        bootstrap_cve_intelligence_async,
        bootstrap_mitre_intelligence_async,
    )
    print("  ✓ Bootstrap functions available")
except Exception as e:
    errors.append(f"Bootstrap import failed: {e}")

# 6. Seed functions
try:
    from db.models.seeds import initialize_default_seed_data
    print("  ✓ Seed functions available")
except Exception as e:
    errors.append(f"Seed import failed: {e}")

if errors:
    print("\n  PREFLIGHT ERRORS:", file=sys.stderr)
    for err in errors:
        print(f"    ✗ {err}", file=sys.stderr)
    sys.exit(1)

print("\n  All pre-flight checks passed.")
PYEOF

  local rc=$?
  if [ $rc -ne 0 ]; then
    _red "✗ Pre-flight checks failed — aborting init"
    exit $rc
  fi
  _green "✓ Pre-flight checks passed"
  echo ""
}

# ==============================================================================
# PHASE 5 — POST-SCHEMA TESTS (DB connection required)
# ==============================================================================
run_postschema_tests() {
  _blue "→ [Phase 5] Running post-schema validation..."

  export CYBERSEC_DB_HOST="$DB_HOST"
  export CYBERSEC_DB_PORT="$DB_PORT"
  export CYBERSEC_DB_USER="$DB_USER"
  export CYBERSEC_DB_PASSWORD="${CYBERSEC_DB_PASSWORD:-}"
  export CYBERSEC_DB_NAME="$DB_NAME"

  cd "$PROJECT_DIR"
  python3 - <<'PYEOF'
import sys, asyncio
sys.path.insert(0, ".")

async def run():
    errors = []

    try:
        from db.bootstrap import get_database_health_async
        health = await get_database_health_async(
            check_connection=True, include_counts=False,
            create_db=False, bootstrap_intel=False,
        )
        if health.get("status") == "error":
            errors.append(f"DB health check failed: {health.get('error')}")
        else:
            tables = health.get("table_count", 0)
            ver = (health.get("database_version") or "").split(",")[0]
            print(f"  ✓ DB connection OK  ({ver})")
            print(f"  ✓ Tables created: {tables}")
            if tables == 0:
                errors.append("No tables found after schema generation")
    except Exception as e:
        errors.append(f"Post-schema check error: {e}")

    if errors:
        print("\n  POST-SCHEMA ERRORS:", file=sys.stderr)
        for err in errors:
            print(f"    ✗ {err}", file=sys.stderr)
        sys.exit(1)

    print("\n  Post-schema validation passed.")

asyncio.run(run())
PYEOF

  local rc=$?
  if [ $rc -ne 0 ]; then
    _red "✗ Post-schema validation failed"
    exit $rc
  fi
  _green "✓ Post-schema validation passed"
  echo ""
}

# ==============================================================================
# PHASE 7 — POST-SEED TESTS (verify intel row counts)
# ==============================================================================
run_postseed_tests() {
  _blue "→ [Phase 7] Running post-seed validation (intel counts)..."

  export CYBERSEC_DB_HOST="$DB_HOST"
  export CYBERSEC_DB_PORT="$DB_PORT"
  export CYBERSEC_DB_USER="$DB_USER"
  export CYBERSEC_DB_PASSWORD="${CYBERSEC_DB_PASSWORD:-}"
  export CYBERSEC_DB_NAME="$DB_NAME"

  cd "$PROJECT_DIR"
  python3 - <<'PYEOF'
import sys, asyncio
sys.path.insert(0, ".")

async def run():
    from db.bootstrap import init_tortoise_async, get_database_health_async

    await init_tortoise_async(create_db=False, bootstrap_intel=False)
    health = await get_database_health_async(
        check_connection=True, include_counts=True,
        create_db=False, bootstrap_intel=False,
    )

    counts = health.get("counts", {})
    total = sum(counts.values())
    print(f"  ✓ Intelligence rows in DB: {total}")
    for key, val in sorted(counts.items()):
        if val > 0:
            print(f"     {key}: {val}")
    if total == 0:
        print("  ℹ  No intel rows yet (run: python3 manage.py seed-intel to populate)")

asyncio.run(run())
PYEOF

  local rc=$?
  if [ $rc -ne 0 ]; then
    _yellow "⚠  Post-seed validation had warnings (non-fatal)"
  else
    _green "✓ Post-seed validation passed"
  fi
  echo ""
}

# ==============================================================================
# --test-only mode: run all test phases and exit
# ==============================================================================
if [ "$TEST_ONLY" -eq 1 ]; then
  _blue "=== TEST-ONLY MODE — no database changes will be made ==="
  echo ""
  run_preflight_tests
  _yellow "Skipping post-schema/seed tests (no DB changes made in test-only mode)"
  echo ""
  _green "✓ Test-only run complete"
  exit 0
fi

# ==============================================================================
# PHASE 0 — Pre-flight (unless skipped)
# ==============================================================================
if [ "$SKIP_TESTS" -eq 0 ]; then
  run_preflight_tests
else
  _yellow "⚠  Pre-flight tests skipped (--skip-tests)"
  echo ""
fi

if [ -n "$DB_SUPERUSER_PASSWORD" ]; then
  export PGPASSWORD="$DB_SUPERUSER_PASSWORD"
fi

# ==============================================================================
# PHASE 1 — Create PostgreSQL user + database (idempotent)
# ==============================================================================
_blue "→ [Phase 1] Creating PostgreSQL user (if not exists)..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -tc \
    "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" | grep -q 1 \
    || psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -c \
    "CREATE USER ${DB_USER} WITH PASSWORD '${CYBERSEC_DB_PASSWORD:-cybersec_default}';"

_blue "→ [Phase 1] Creating database (if not exists)..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -tc \
    "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1 \
    || psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -c \
    "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"

# ==============================================================================
# PHASE 2 — Grant permissions
# ==============================================================================
_blue "→ [Phase 2] Granting database permissions..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -c \
    "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"

# ==============================================================================
# PHASE 3 — Enable PostgreSQL extensions
# ==============================================================================
_blue "→ [Phase 3] Enabling PostgreSQL extensions for forensic analysis..."
psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_SUPERUSER" -c \
    "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"           || true
psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_SUPERUSER" -c \
    "CREATE EXTENSION IF NOT EXISTS \"pg_stat_statements\";"  || true
psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_SUPERUSER" -c \
    "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";"             || true
psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_SUPERUSER" -c \
    "CREATE EXTENSION IF NOT EXISTS \"btree_gin\";"           || true

# ==============================================================================
# PHASE 4 — Create all tables via generate_schemas
# ==============================================================================
_blue "→ [Phase 4] Creating database schema (Tortoise generate_schemas)..."
cd "$PROJECT_DIR"
CYBERSEC_AUTO_CREATE_DB=1 python3 manage.py schema

# ==============================================================================
# PHASE 5 — Post-schema tests
# ==============================================================================
if [ "$SKIP_TESTS" -eq 0 ]; then
  run_postschema_tests
else
  _yellow "⚠  Post-schema tests skipped (--skip-tests)"
  echo ""
fi

# ==============================================================================
# PHASE 6 — Seed default data
# ==============================================================================
if [ "$SKIP_SEED" -eq 0 ]; then
  _blue "→ [Phase 6] Seeding default forensic data..."
  python3 manage.py seed || _yellow "Warning: Seeding skipped (models not yet ready?)"
else
  _yellow "⚠  Seed phase skipped (--skip-seed)"
fi
echo ""

# ==============================================================================
# PHASE 7 — Post-seed intel count validation
# ==============================================================================
if [ "$SKIP_TESTS" -eq 0 ]; then
  run_postseed_tests
else
  _yellow "⚠  Post-seed tests skipped (--skip-tests)"
  echo ""
fi

# ==============================================================================
# PHASE 8 — Performance indexes
# ==============================================================================
if [ "$SKIP_INDEXES" -eq 0 ]; then
  _blue "→ [Phase 8] Creating performance indexes (FK + GIN/trgm — not in Tortoise ORM Meta)..."
  psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_USER" <<'SQL' || true
-- GIN trigram index for fast substring/fuzzy search on IOC values
CREATE INDEX IF NOT EXISTS idx_ioc_entries_value_trgm ON ioc_entries USING gin(value gin_trgm_ops);
-- GIN full-text search index on finding descriptions
CREATE INDEX IF NOT EXISTS idx_findings_description_fts ON findings USING gin(to_tsvector('english', description));

-- FK indexes: Tortoise ORM does not add db-level indexes for ForeignKeyFields by default.
-- These are required for all join/filter operations on FK columns.
CREATE INDEX IF NOT EXISTS idx_api_account_provider_id ON api_account(provider_id);
CREATE INDEX IF NOT EXISTS idx_artifact_signature_logs_artifact_id ON artifact_signature_logs(artifact_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_parent_version_id ON artifacts(parent_version_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_session_id ON audit_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_baselines_session_id ON baselines(session_id);
CREATE INDEX IF NOT EXISTS idx_case_intakes_session_id ON case_intakes(session_id);
CREATE INDEX IF NOT EXISTS idx_certificates_session_id ON certificates(session_id);
CREATE INDEX IF NOT EXISTS idx_certificates_domain_id ON certificates(domain_id);
CREATE INDEX IF NOT EXISTS idx_cleared_items_original_watchlist_id ON cleared_items(original_watchlist_id);
CREATE INDEX IF NOT EXISTS idx_cleared_items_original_ioc_id ON cleared_items(original_ioc_id);
CREATE INDEX IF NOT EXISTS idx_cleared_items_cleared_by_session_id ON cleared_items(cleared_by_session_id);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_rule_id ON compliance_checks(rule_id);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_session_id ON compliance_checks(session_id);
CREATE INDEX IF NOT EXISTS idx_cpu_info_machine_id ON cpu_info(machine_id);
CREATE INDEX IF NOT EXISTS idx_domains_session_id ON domains(session_id);
CREATE INDEX IF NOT EXISTS idx_domains_host_id ON domains(host_id);
CREATE INDEX IF NOT EXISTS idx_finding_host_findings_id ON finding_host(findings_id);
CREATE INDEX IF NOT EXISTS idx_finding_host_host_id ON finding_host(host_id);
CREATE INDEX IF NOT EXISTS idx_finding_ioc_ioc_id ON finding_ioc(ioc_id);
CREATE INDEX IF NOT EXISTS idx_finding_ioc_findings_id ON finding_ioc(findings_id);
CREATE INDEX IF NOT EXISTS idx_findings_mitre_mitretechnique_id ON findings_mitre_techniques(mitretechnique_id);
CREATE INDEX IF NOT EXISTS idx_findings_mitre_findings_id ON findings_mitre_techniques(findings_id);
CREATE INDEX IF NOT EXISTS idx_fft_forensic_findings_id ON forensic_finding_techniques(forensic_findings_id);
CREATE INDEX IF NOT EXISTS idx_fft_forensicmitretechnique_id ON forensic_finding_techniques(forensicmitretechnique_id);
CREATE INDEX IF NOT EXISTS idx_fffa_forensic_findings_id ON forensic_findings_forensic_artifacts(forensic_findings_id);
CREATE INDEX IF NOT EXISTS idx_fffa_forensicartifact_id ON forensic_findings_forensic_artifacts(forensicartifact_id);
CREATE INDEX IF NOT EXISTS idx_ffie_iocentry_id ON forensic_findings_ioc_entries(iocentry_id);
CREATE INDEX IF NOT EXISTS idx_ffie_forensic_findings_id ON forensic_findings_ioc_entries(forensic_findings_id);
CREATE INDEX IF NOT EXISTS idx_forensic_projects_scope_project_id ON forensic_projects(scope_project_id);
CREATE INDEX IF NOT EXISTS idx_forensic_sessions_scope_session_id ON forensic_sessions(scope_session_id);
CREATE INDEX IF NOT EXISTS idx_fwi_added_by_session_id ON forensic_watchlist_items(added_by_session_id);
CREATE INDEX IF NOT EXISTS idx_fwi_last_checked_session_id ON forensic_watchlist_items(last_checked_session_id);
CREATE INDEX IF NOT EXISTS idx_fwi_escalated_to_ioc_id ON forensic_watchlist_items(escalated_to_ioc_id);
CREATE INDEX IF NOT EXISTS idx_host_ip_addresses_hosts_id ON host_ip_addresses(hosts_id);
CREATE INDEX IF NOT EXISTS idx_host_ip_addresses_ipaddress_id ON host_ip_addresses(ipaddress_id);
CREATE INDEX IF NOT EXISTS idx_hosts_session_id ON hosts(session_id);
CREATE INDEX IF NOT EXISTS idx_iasr_actor_id ON intel_actor_software_refs(actor_id);
CREATE INDEX IF NOT EXISTS idx_iasr_software_id ON intel_actor_software_refs(software_id);
CREATE INDEX IF NOT EXISTS idx_iatr_actor_id ON intel_actor_technique_refs(actor_id);
CREATE INDEX IF NOT EXISTS idx_iatr_technique_id ON intel_actor_technique_refs(technique_id);
CREATE INDEX IF NOT EXISTS idx_icmr_technique_id ON intel_capec_mitre_refs(technique_id);
CREATE INDEX IF NOT EXISTS idx_icmr_capec_id ON intel_capec_mitre_refs(capec_id);
CREATE INDEX IF NOT EXISTS idx_iccr_cve_id ON intel_cve_cwe_refs(cve_id);
CREATE INDEX IF NOT EXISTS idx_iccr_cwe_id ON intel_cve_cwe_refs(cwe_id);
CREATE INDEX IF NOT EXISTS idx_intel_cve_entries_cve_id ON intel_cve_entries(cve_id);
CREATE INDEX IF NOT EXISTS idx_icvemr_cve_id ON intel_cve_mitre_refs(cve_id);
CREATE INDEX IF NOT EXISTS idx_icvemr_technique_id ON intel_cve_mitre_refs(technique_id);
CREATE INDEX IF NOT EXISTS idx_icsecr_cwe_id ON intel_cwe_capec_refs(cwe_id);
CREATE INDEX IF NOT EXISTS idx_icsecr_capec_id ON intel_cwe_capec_refs(capec_id);
CREATE INDEX IF NOT EXISTS idx_ima_event_id ON intel_misp_attributes(event_id);
CREATE INDEX IF NOT EXISTS idx_ima_source_snapshot_id ON intel_misp_attributes(source_snapshot_id);
CREATE INDEX IF NOT EXISTS idx_ime_source_snapshot_id ON intel_misp_events(source_snapshot_id);
CREATE INDEX IF NOT EXISTS idx_ioe_source_snapshot_id ON intel_opencti_entities(source_snapshot_id);
CREATE INDEX IF NOT EXISTS idx_ioi_source_snapshot_id ON intel_opencti_indicators(source_snapshot_id);
CREATE INDEX IF NOT EXISTS idx_istr_software_id ON intel_software_technique_refs(software_id);
CREATE INDEX IF NOT EXISTS idx_istr_technique_id ON intel_software_technique_refs(technique_id);
CREATE INDEX IF NOT EXISTS idx_itpe_actor_id ON intel_threat_profile_entries(actor_id);
CREATE INDEX IF NOT EXISTS idx_interface_addresses_interface_id ON interface_addresses(interface_id);
CREATE INDEX IF NOT EXISTS idx_ioc_entries_last_session_id ON ioc_entries(last_session_id);
CREATE INDEX IF NOT EXISTS idx_ioc_entries_intel_match_id ON ioc_entries(intel_match_id);
CREATE INDEX IF NOT EXISTS idx_iocs_intel_match_id ON iocs(intel_match_id);
CREATE INDEX IF NOT EXISTS idx_iocs_session_id ON iocs(session_id);
CREATE INDEX IF NOT EXISTS idx_kernel_baselines_session_id ON kernel_baselines(session_id);
CREATE INDEX IF NOT EXISTS idx_kernel_modules_kernel_id ON kernel_modules(kernel_id);
CREATE INDEX IF NOT EXISTS idx_kernels_session_id ON kernels(session_id);
CREATE INDEX IF NOT EXISTS idx_machines_host_id ON machines(host_id);
CREATE INDEX IF NOT EXISTS idx_memory_modules_machine_id ON memory_modules(machine_id);
CREATE INDEX IF NOT EXISTS idx_mitre_techniques_finding_id ON mitre_techniques(finding_id);
CREATE INDEX IF NOT EXISTS idx_mitre_techniques_session_id ON mitre_techniques(session_id);
CREATE INDEX IF NOT EXISTS idx_network_baselines_session_id ON network_baselines(session_id);
CREATE INDEX IF NOT EXISTS idx_network_connections_session_id ON network_connections(session_id);
CREATE INDEX IF NOT EXISTS idx_network_interfaces_machine_id ON network_interfaces(machine_id);
CREATE INDEX IF NOT EXISTS idx_pci_devices_machine_id ON pci_devices(machine_id);
CREATE INDEX IF NOT EXISTS idx_persistence_baselines_session_id ON persistence_baselines(session_id);
CREATE INDEX IF NOT EXISTS idx_process_baselines_session_id ON process_baselines(session_id);
CREATE INDEX IF NOT EXISTS idx_provider_auth_methods_provider_id ON provider_auth_methods(provider_id);
CREATE INDEX IF NOT EXISTS idx_risks_session_id ON risks(session_id);
CREATE INDEX IF NOT EXISTS idx_scoped_entries_session_id ON scoped_entries(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_project_id ON sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_shared_entries_session_id ON shared_entries(session_id);
CREATE INDEX IF NOT EXISTS idx_storage_drives_machine_id ON storage_drives(machine_id);
CREATE INDEX IF NOT EXISTS idx_storage_partitions_drive_id ON storage_partitions(drive_id);
CREATE INDEX IF NOT EXISTS idx_timeline_entries_ioc_reference_id ON timeline_entries(ioc_reference_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_session_discovered_id ON vulnerabilities(session_discovered_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_session_id ON watchlist_items(session_id);
CREATE INDEX IF NOT EXISTS idx_yara_rules_generated_by_session_id ON yara_rules(generated_by_session_id);
CREATE INDEX IF NOT EXISTS idx_yara_test_runs_rule_id ON yara_test_runs(rule_id);
CREATE INDEX IF NOT EXISTS idx_yara_test_runs_session_id ON yara_test_runs(session_id);

-- Composite PKs for M2M junction tables (Tortoise ORM omits these)
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='finding_host'::regclass AND contype='p') THEN
    ALTER TABLE finding_host ADD PRIMARY KEY (findings_id, host_id); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='finding_ioc'::regclass AND contype='p') THEN
    ALTER TABLE finding_ioc ADD PRIMARY KEY (findings_id, ioc_id); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='findings_mitre_techniques'::regclass AND contype='p') THEN
    ALTER TABLE findings_mitre_techniques ADD PRIMARY KEY (findings_id, mitretechnique_id); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='forensic_finding_techniques'::regclass AND contype='p') THEN
    ALTER TABLE forensic_finding_techniques ADD PRIMARY KEY (forensic_findings_id, forensicmitretechnique_id); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='forensic_findings_forensic_artifacts'::regclass AND contype='p') THEN
    ALTER TABLE forensic_findings_forensic_artifacts ADD PRIMARY KEY (forensic_findings_id, forensicartifact_id); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='forensic_findings_ioc_entries'::regclass AND contype='p') THEN
    ALTER TABLE forensic_findings_ioc_entries ADD PRIMARY KEY (forensic_findings_id, iocentry_id); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='host_ip_addresses'::regclass AND contype='p') THEN
    ALTER TABLE host_ip_addresses ADD PRIMARY KEY (hosts_id, ipaddress_id); END IF;
END $$;

-- CHECK constraints for enum-like varchar columns
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_anti_forensic_techniques_severity') THEN
    ALTER TABLE anti_forensic_techniques ADD CONSTRAINT chk_anti_forensic_techniques_severity CHECK (severity IN ('info','low','medium','high','critical')); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_anti_forensic_techniques_confidence') THEN
    ALTER TABLE anti_forensic_techniques ADD CONSTRAINT chk_anti_forensic_techniques_confidence CHECK (confidence IN ('low','medium','high','confirmed')); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_compliance_rules_severity') THEN
    ALTER TABLE compliance_rules ADD CONSTRAINT chk_compliance_rules_severity CHECK (severity IN ('info','low','medium','high','critical')); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_intel_cwes_status') THEN
    ALTER TABLE intel_cwes ADD CONSTRAINT chk_intel_cwes_status CHECK (status IN ('open','patched','mitigated','accepted','false_positive','active','deprecated','draft')); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_intel_ioc_db_entries_confidence') THEN
    ALTER TABLE intel_ioc_db_entries ADD CONSTRAINT chk_intel_ioc_db_entries_confidence CHECK (confidence IN ('low','medium','high','confirmed')); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_intel_pocs_severity') THEN
    ALTER TABLE intel_pocs ADD CONSTRAINT chk_intel_pocs_severity CHECK (severity IN ('info','low','medium','high','critical')); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_ioc_entries_confidence') THEN
    ALTER TABLE ioc_entries ADD CONSTRAINT chk_ioc_entries_confidence CHECK (confidence IN ('low','medium','high','confirmed')); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_ioc_entries_severity') THEN
    ALTER TABLE ioc_entries ADD CONSTRAINT chk_ioc_entries_severity CHECK (severity IN ('info','low','medium','high','critical')); END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='chk_vulnerabilities_severity') THEN
    ALTER TABLE vulnerabilities ADD CONSTRAINT chk_vulnerabilities_severity CHECK (severity IN ('info','low','medium','high','critical')); END IF;
END $$;
SQL
  _green "✓ Performance indexes, junction PKs, and CHECK constraints applied"
else
  _yellow "⚠  Performance indexes skipped (--skip-indexes)"
fi
echo ""

# ==============================================================================
# PHASE 9 — Create database backup script
# ==============================================================================
_blue "→ [Phase 9] Creating database backup script..."
cat > "$PROJECT_DIR/scripts/backup_db.sh" <<'EOF'
#!/usr/bin/env bash
# Database backup script for forensic evidence preservation
set -euo pipefail

DB_NAME="${CYBERSEC_DB_NAME:-cybersec_forensics}"
DB_HOST="${CYBERSEC_DB_HOST:-127.0.0.1}"
DB_PORT="${CYBERSEC_DB_PORT:-5432}"
DB_USER="${CYBERSEC_DB_USER:-cybersec}"
BACKUP_DIR="${CYBERSEC_BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "Creating forensic database backup..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --create --clean --if-exists --verbose \
    --file="$BACKUP_DIR/cybersec_forensics_${TIMESTAMP}.sql"

gzip "$BACKUP_DIR/cybersec_forensics_${TIMESTAMP}.sql"
echo "Backup completed: $BACKUP_DIR/cybersec_forensics_${TIMESTAMP}.sql.gz"
EOF
chmod +x "$PROJECT_DIR/scripts/backup_db.sh"

# ==============================================================================
# PHASE 10 — Final status summary
# ==============================================================================
_blue "→ [Phase 10] Final database status..."
cd "$PROJECT_DIR" && python3 manage.py status

echo ""
_green "✅ CyberSec Database Ready: ${DB_NAME}"
echo ""
echo "🔧 Available commands:"
echo "   python3 manage.py schema    - Recreate/update tables"
echo "   python3 manage.py status    - Show table list + intel counts"
echo "   python3 manage.py seed      - Seed MITRE + compliance data"
echo "   python3 manage.py seed-intel - Bootstrap intel only"
echo "   python3 manage.py drop      - Drop all tables (destructive!)"
echo ""
echo "🧪 Test commands:"
echo "   ./scripts/init_db.sh --test-only   - Pre-flight checks only"
echo "   ./scripts/init_db.sh --skip-tests  - Skip all test gates"
echo ""
