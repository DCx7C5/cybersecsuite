#!/usr/bin/env bash
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
  _blue "→ [Phase 8] Creating special indexes (GIN/trgm — not expressible in Tortoise ORM)..."
  psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_USER" <<'SQL' || true
-- GIN trigram index for fast substring/fuzzy search on IOC values
-- (requires pg_trgm extension; cannot be declared in Tortoise model Meta)
CREATE INDEX IF NOT EXISTS idx_ioc_entries_value_trgm
    ON ioc_entries USING gin(value gin_trgm_ops);

-- GIN full-text search index on finding descriptions
-- (requires to_tsvector; cannot be declared in Tortoise model Meta)
CREATE INDEX IF NOT EXISTS idx_findings_description_fts
    ON findings USING gin(to_tsvector('english', description));
SQL
  _green "✓ Special GIN indexes created"
else
  _yellow "⚠  Special indexes skipped (--skip-indexes)"
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
