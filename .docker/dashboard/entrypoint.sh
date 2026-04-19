#!/bin/bash
set -e

echo "[dashboard-init] Starting CyberSec Dashboard initialization..."

# Wait for postgres to be ready via TCP or Unix socket
PG_HOST="${CYBERSEC_DB_HOST:-localhost}"
PG_PORT="${CYBERSEC_DB_PORT:-5432}"

if [[ "$PG_HOST" == /* ]]; then
    # Unix socket mode — wait for the socket file
    SOCKET_FILE="${PG_HOST}/.s.PGSQL.${PG_PORT}"
    echo "[dashboard-init] Waiting for PostgreSQL socket at $SOCKET_FILE..."
    for i in {1..30}; do
        if [ -S "$SOCKET_FILE" ] 2>/dev/null; then
            echo "[dashboard-init] ✓ PostgreSQL socket found"
            break
        fi
        echo "[dashboard-init] Waiting... ($i/30)"
        sleep 1
    done
else
    # TCP mode — wait for the port
    echo "[dashboard-init] Waiting for PostgreSQL at $PG_HOST:$PG_PORT..."
    for i in {1..30}; do
        if pg_isready -h "$PG_HOST" -p "$PG_PORT" -q 2>/dev/null; then
            echo "[dashboard-init] ✓ PostgreSQL is ready"
            break
        fi
        echo "[dashboard-init] Waiting... ($i/30)"
        sleep 1
    done
fi

# Create database schemas
echo "[dashboard-init] Creating database schemas..."
if python3 src/manage.py schema; then
    echo "[dashboard-init] ✓ Schemas created successfully"
else
    echo "[dashboard-init] ✗ Schema creation failed (may already exist)"
fi

# Bootstrap intelligence data (optional, can be slow)
echo "[dashboard-init] Bootstrapping intelligence data..."
if python3 src/manage.py seed-intel 2>&1 | head -20; then
    echo "[dashboard-init] ✓ Intelligence data loaded"
else
    echo "[dashboard-init] ⚠ Intelligence bootstrap encountered issues (check logs)"
fi

echo "[dashboard-init] ✓ Initialization complete"
echo "[dashboard-init] Starting ASGI server (uvicorn) on port ${ASGI_PORT:-8000}..."
echo ""

# Start the ASGI server (includes dashboard at /dashboard/*, proxy at /v1/*, A2A at /a2a)
exec uv run uvicorn proxy.asgi:app \
    --host "${ASGI_HOST:-0.0.0.0}" \
    --port "${ASGI_PORT:-8000}" \
    --log-level info

