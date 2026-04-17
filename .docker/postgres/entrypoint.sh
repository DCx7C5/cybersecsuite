#!/usr/bin/env bash
set -euo pipefail

echo "[cybersec-postgres] Starting with custom 8GB RAM configuration (Alpine)..."

# Offizielles EntryPoint aufrufen und unsere Config übergeben
# Strip a leading bare "postgres" word from $@ if present
# (docker-compose command: starts with "postgres" which is redundant here)
ARGS=("$@")
if [ "${ARGS[0]:-}" = "postgres" ]; then
    ARGS=("${ARGS[@]:1}")
fi

exec docker-entrypoint.sh postgres \
    -c config_file=/etc/postgresql/postgresql.conf \
    "${ARGS[@]}"
