#!/bin/bash
set -e

echo "[dashboard-init] Starting CyberSec Dashboard initialization..."

# Wait for postgres to be ready
echo "[dashboard-init] Waiting for PostgreSQL socket at $CYBERSEC_DB_HOST..."
for i in {1..30}; do
    if [ -S "$CYBERSEC_DB_HOST" ] 2>/dev/null; then
        echo "[dashboard-init] ✓ PostgreSQL socket found"
        break
    fi
    echo "[dashboard-init] Waiting... ($i/30)"
    sleep 1
done

# Create database schemas
echo "[dashboard-init] Creating database schemas..."
if python3 manage.py schema; then
    echo "[dashboard-init] ✓ Schemas created successfully"
else
    echo "[dashboard-init] ✗ Schema creation failed (may already exist)"
fi

# Bootstrap intelligence data (optional, can be slow)
echo "[dashboard-init] Bootstrapping intelligence data..."
if python3 manage.py seed-intel 2>&1 | head -20; then
    echo "[dashboard-init] ✓ Intelligence data loaded"
else
    echo "[dashboard-init] ⚠ Intelligence bootstrap encountered issues (check logs)"
fi

echo "[dashboard-init] ✓ Initialization complete"
echo "[dashboard-init] Starting Dashboard server on port 8322..."
echo ""

# Start the dashboard
exec python3 manage.py dashboard --serve --port 8322

