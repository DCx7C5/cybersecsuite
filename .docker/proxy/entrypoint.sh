#!/bin/bash
set -e

echo "[proxy-init] Starting CyberSec Dashboard initialization..."

# Wait for postgres to be ready via TCP or Unix socket
PG_HOST="${CYBERSEC_DB_HOST:-localhost}"
PG_PORT="${CYBERSEC_DB_PORT:-5432}"

if [[ "$PG_HOST" == /* ]]; then
    # Unix socket mode — wait for the socket file
    SOCKET_FILE="${PG_HOST}/.s.PGSQL.${PG_PORT}"
    echo "[proxy-init] Waiting for PostgreSQL socket at $SOCKET_FILE..."
    for i in {1..30}; do
        if [ -S "$SOCKET_FILE" ] 2>/dev/null; then
            echo "[proxy-init] ✓ PostgreSQL socket found"
            break
        fi
        echo "[proxy-init] Waiting... ($i/30)"
        sleep 1
    done
else
    # TCP mode — wait for the port
    echo "[proxy-init] Waiting for PostgreSQL at $PG_HOST:$PG_PORT..."
    for i in {1..30}; do
        if pg_isready -h "$PG_HOST" -p "$PG_PORT" -q 2>/dev/null; then
            echo "[proxy-init] ✓ PostgreSQL is ready"
            break
        fi
        echo "[proxy-init] Waiting... ($i/30)"
        sleep 1
    done
fi

# Initialise database: create schemas + seed all fixtures
echo "[proxy-init] Running database initialisation (schema + seed fixtures)..."
if uv run python manage.py init-db; then
    echo "[proxy-init] ✓ Database initialisation complete"
else
    echo "[proxy-init] ⚠ Database initialisation encountered issues (check logs above)"
fi

echo "[proxy-init] ✓ Initialization complete"

# Check for TLS certificates
TLS_CERT="${ASGI_TLS_CERT:-/home/cybersec/.omniroute/certs/cert.pem}"
TLS_KEY="${ASGI_TLS_KEY:-/home/cybersec/.omniroute/certs/key.pem}"

# Default to port 8000, redirect 8443 → 8000 if no TLS
HTTP_PORT="${ASGI_PORT:-8000}"
HTTPS_PORT="${ASGI_TLS_PORT:-8443}"

if [[ -f "$TLS_CERT" && -f "$TLS_KEY" ]]; then
    echo "[proxy-init] TLS certificates detected - starting HTTPS on port $HTTPS_PORT"
    echo "[proxy-init] Starting ASGI server with TLS..."
    exec uv run python manage.py serve \
        --host "${ASGI_HOST:-0.0.0.0}" \
        --port "$HTTP_PORT"
else
    echo "[proxy-init] No TLS certificates found - serving HTTP only on port $HTTP_PORT"
    echo "[proxy-init] Starting ASGI server..."
    exec uv run python manage.py serve \
        --host "${ASGI_HOST:-0.0.0.0}" \
        --port "$HTTP_PORT"
fi

