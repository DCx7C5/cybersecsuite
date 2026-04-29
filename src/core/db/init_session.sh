#!/usr/bin/env bash
# DEPRECATED: This script is no longer maintained.
# Use the Python management command instead: uv run python -m manage init-session
# Cybersec Forensic Session Initialization
set -euo pipefail

SESSION_ID="$(date +%Y%m%d_%H%M%S)"
SESSION_DIR="./cybersec-sessions/$SESSION_ID"
SHARED_DIR="./data/cybersec-shared"

echo "🔐 Initializing Forensic Session: $SESSION_ID"

# Create session directory structure
mkdir -p "$SESSION_DIR"/{live,artifacts,analysis,response,hardening,anti-forensics,meta}

# Initialize shared memory if needed
if [ ! -d "$SHARED_DIR" ]; then
  echo "Initializing shared forensic intelligence store..."
  mkdir -p "$SHARED_DIR"/{intelligence,forensics,defense,attack-surface,hardening,baselines,sessions,meta}
  
  # Create core intelligence files
  touch "$SHARED_DIR/intelligence/ioc-db.md"
  touch "$SHARED_DIR/intelligence/threat-profile.md"
  touch "$SHARED_DIR/meta/watchlist.md"
  touch "$SHARED_DIR/meta/cleared.md"
  
  # Create session index
  {
    echo "# Session Index"
    echo "| Session ID | Date | Agent | Phase | IOCs | New IOCs | Verdict | Path |"
    echo "|------------|------|-------|-------|------|----------|---------|------|"
  } > "$SHARED_DIR/sessions/session-index.md"
fi

# Load threat intelligence
IOC_COUNT=$(grep -c "^|" "$SHARED_DIR/intelligence/ioc-db.md" 2>/dev/null || echo "0")
WATCHLIST_COUNT=$(grep -c "^|" "$SHARED_DIR/meta/watchlist.md" 2>/dev/null || echo "0")
CLEARED_COUNT=$(grep -c "^|" "$SHARED_DIR/meta/cleared.md" 2>/dev/null || echo "0")

# Check for recent threat intelligence updates
LAST_UPDATE="Never"
if [ -f "$SHARED_DIR/meta/last-intel-update.txt" ]; then
  LAST_UPDATE_TS=$(cat "$SHARED_DIR/meta/last-intel-update.txt")
  LAST_UPDATE=$(date -d "@$(date -d "$LAST_UPDATE_TS" +%s 2>/dev/null || echo 0)" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "$LAST_UPDATE_TS")
fi

# Create session manifest
cat > "$SESSION_DIR/meta/session-manifest.json" <<JSON
{
  "session_id": "$SESSION_ID",
  "start_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "agent": "malwarehunter-elite",
  "framework_version": "3.0",
  "intelligence_loaded": {
    "iocs": $IOC_COUNT,
    "watchlist": $WATCHLIST_COUNT,
    "cleared": $CLEARED_COUNT,
    "last_update": "$LAST_UPDATE"
  },
  "capabilities": [
    "real-time-ioc-correlation",
    "anti-forensic-detection",
    "evidence-preservation",
    "progressive-hardening",
    "threat-intelligence-sync",
    "mitre-attack-mapping",
    "cve-vulnerability-correlation",
    "cwe-weakness-analysis"
  ]
}
JSON

echo "✅ Session $SESSION_ID initialized"
echo "   IOCs loaded: $IOC_COUNT"
echo "   Watchlist: $WATCHLIST_COUNT"
echo "   Cleared: $CLEARED_COUNT"
echo "   Threat intel: $LAST_UPDATE"
echo "   Session path: $SESSION_DIR"
