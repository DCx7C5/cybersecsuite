# CyberSec Database Lifecycle Management

Production-grade PostgreSQL lifecycle tools for forensic intelligence framework.

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `init_db.sh` | Initialize/reset database schema via Tortoise ORM | `./db/init_db.sh [--skip-tests] [--skip-seed]` |
| `backup_db.sh` | Create timestamped forensic backup (gzipped SQL) | `./db/backup_db.sh` |
| `init_session.sh` | Initialize forensic investigation session metadata | `./db/init_session.sh` |

## Environment Variables

```bash
# Database connection
export CYBERSEC_DB_HOST=127.0.0.1           # or /tmp/.s.PGSQL. for socket
export CYBERSEC_DB_PORT=5432
export CYBERSEC_DB_USER=cybersec
export CYBERSEC_DB_PASSWORD=cybersec_default
export CYBERSEC_DB_NAME=cybersec_forensics

# Backup location
export CYBERSEC_BACKUP_DIR=./backups

# Auto-create DB (used by manage.py)
export CYBERSEC_AUTO_CREATE_DB=1
```

## Quick Start

```bash
# 1. Initialize database (creates user, DB, schema, seeds intel)
./db/init_db.sh

# 2. Create backup before any changes
./db/backup_db.sh

# 3. Initialize a new forensic session
./db/init_session.sh

# 4. Check database health
python3 manage.py status
```

## Schema Management

No migrations — schema is driven by model definitions via `Tortoise.generate_schemas(safe=True)`.

### When models change:
```bash
python3 manage.py drop     # Drop all tables
python3 manage.py schema   # Recreate from models
python3 manage.py seed     # Bootstrap MITRE + compliance data
```

### Available manage.py commands:
```bash
python3 manage.py schema       # Create/update schema
python3 manage.py status       # Show table counts + intel rows
python3 manage.py seed         # Bootstrap default data
python3 manage.py seed-intel   # Bootstrap intel only
python3 manage.py drop         # Drop all tables (destructive!)
```

## Backup & Restore

```bash
# Backup
./db/backup_db.sh    # Creates backups/cybersec_forensics_YYYYMMDD_HHMMSS.sql.gz

# Restore
gunzip backups/cybersec_forensics_YYYYMMDD_HHMMSS.sql.gz
psql -h localhost -U cybersec < backups/cybersec_forensics_YYYYMMDD_HHMMSS.sql
```

## Socket vs TCP

### Unix Socket (recommended for local dev)
```bash
export CYBERSEC_DB_HOST=/tmp/.s.PGSQL.   # or /var/run/postgresql
export CYBERSEC_DB_PORT=5432              # ignored for sockets
```

### TCP/IP
```bash
export CYBERSEC_DB_HOST=127.0.0.1
export CYBERSEC_DB_PORT=5432
```

## Docker Compose (optional)

```bash
docker-compose up -d postgres     # Start PostgreSQL container
./db/init_db.sh                    # Initialize schema
```

## Testing

```bash
# Run all tests with coverage
uv run --group test pytest --cov=db

# Pre-flight checks only (no DB changes)
./db/init_db.sh --test-only

# Skip all tests
./db/init_db.sh --skip-tests
```

## Forensic Evidence Preservation

All backups are timestamped and gzipped for integrity:
- Chain of custody via file modification timestamps
- SQL dump includes schema + data + constraints
- Compatible with all PostgreSQL versions ≥ 12

## Key Files

- `bootstrap.py` — Database initialization + health checks
- `intel_loader.py` — MITRE ATT&CK + CVE/CWE/CAPEC intelligence bootstrap
- `settings.py` — DB connection config from env vars
- `models/` — Tortoise ORM model definitions (~50 models across 30 files)

## Model Reference

| File | Models / Domain |
|------|----------------|
| `core.py` | `Workspace`, `Project`, `Session` |
| `scope.py` | `ScopeContext` |
| `investigation.py` | `Investigation`, `Phase` |
| `case_intake.py` | `Case`, `CaseIntake` |
| `forensic.py` | `ForensicArtifact`, `ForensicTimeline` |
| `ioc.py` | `IOC` |
| `ioc_entry.py` | `IOCEntry` |
| `intelligence.py` | `IntelligenceReport` |
| `threat_intel.py` | `ThreatIntelEntry` |
| `threat_profile_entry.py` | `ThreatProfileEntry` |
| `mitre_technique.py` | `MitreAttackTechnique` |
| `mitre_actor.py` | `MitreActor` |
| `mitre_software.py` | `MitreSoftware` |
| `cve.py` | `CVEFinding` |
| `cve_entry.py` | `CVEEntry` |
| `cwe.py` | `CWEEntry` |
| `capec.py` | `CAPECEntry` |
| `compliance.py` | `ComplianceControl`, `ComplianceResult` |
| `defense.py` | `DefenseRecommendation` |
| `vulnerability.py` | `VulnerabilityEntry` |
| `network.py` | `NetworkConnection`, `NetworkHost` |
| `kernel.py` | `KernelModule`, `KernelSyscall` |
| `baselines.py` | `SystemBaseline` |
| `artifact.py` | `Artifact` |
| `artifacts.py` | `ArtifactSignature` |
| `audit.py` | `AuditLog` |
| `api_usage_log.py` | `ApiUsageLog` |
| `a2a_task.py` | `A2ATask` |
| `yara_rule.py` | `YaraRule` |
| `layers.py` | `ContextLayer` |
| `tag.py` | `Tag` |
| `references.py` | `Reference` |
| `machine.py` | `MachineInventory` |
| `feed_snapshot.py` | `FeedSnapshot` |
| `update_log_entry.py` | `UpdateLogEntry` |
| `user_guidance.py` | `UserGuidance` |
| `opencti.py` | `OpenCTIEntry` |
| `misp.py` | `MISPEvent` |
| `permission_checker.py` | `PermissionCheck` |
| `seeds.py` | Seed data helpers |

## Intelligence Bootstrap

`intel_loader.py` bootstraps threat intelligence from public sources:

| Dataset | Records | Source |
|---------|---------|--------|
| MITRE ATT&CK | ~900 techniques | STIX JSON |
| CVE | ~250K entries | NVD JSON feed |
| CWE | ~900 weaknesses | MITRE XML |
| CAPEC | ~500 patterns | MITRE XML |

Run once: `make seed-intel` (or `make seed` for all data including defaults). After seeding, set `CYBERSEC_BOOTSTRAP_INTEL_ON_START=false`.

