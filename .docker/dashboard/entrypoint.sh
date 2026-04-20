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

# Check for TLS certificates
TLS_CERT="${ASGI_TLS_CERT:-/home/cybersec/.omniroute/certs/cert.pem}"
TLS_KEY="${ASGI_TLS_KEY:-/home/cybersec/.omniroute/certs/key.pem}"

# Default to port 8000, redirect 8443 → 8000 if no TLS
HTTP_PORT="${ASGI_PORT:-8000}"
HTTPS_PORT="${ASGI_TLS_PORT:-8443}"

if [[ -f "$TLS_CERT" && -f "$TLS_KEY" ]]; then
    echo "[dashboard-init] TLS certificates detected - starting HTTPS on port $HTTPS_PORT"
    echo "[dashboard-init] Starting ASGI server with TLS..."
    exec uv run uvicorn proxy.asgi:app \
        --host "${ASGI_HOST:-0.0.0.0}" \
        --port "$HTTP_PORT" \
        --ssl-keyfile "$TLS_KEY" \
        --ssl-certfile "$TLS_CERT" \
        --log-level info
else
    echo "[dashboard-init] No TLS certificates found - serving HTTP only on port $HTTP_PORT"
    echo "[dashboard-init] Redirect from port $HTTPS_PORT is handled by docker-compose (not exposed)"
    echo "[dashboard-init] Starting ASGI server..."
    exec uv run uvicorn proxy.asgi:app \
        --host "${ASGI_HOST:-0.0.0.0}" \
        --port "$HTTP_PORT" \
        --log-level info
fi

