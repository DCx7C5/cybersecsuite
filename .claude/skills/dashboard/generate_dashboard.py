#!/usr/bin/env python3
"""
CyberSec Dashboard Generator
─────────────────────────────
Collects live data from DB + settings.json and writes a self-contained
index.html to skills/dashboard/index.html.

Usage:
  python3 skills/dashboard/generate_dashboard.py # generate only
  python3 skills/dashboard/generate_dashboard.py --open # generate and open browser
  python3 skills/dashboard/generate_dashboard.py --serve # generate and HTTP server (port 8322)
  python3 skills/dashboard/generate_dashboard.py --serve --port 9000
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ── Load .env if present (sets CYBERSEC_DB_* env vars before any DB import) ──
def _load_dotenv() -> None:
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return
    import os
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:   # don't overwrite existing env
            os.environ[key] = value

_load_dotenv()

DASHBOARD_DIR = Path(__file__).resolve().parent
OUT_FILE = DASHBOARD_DIR / "index.html"


# ──────────────────────────────────────────────────────────────────────────────
# Data collection
# ──────────────────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    path = PROJECT_ROOT / "settings.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def load_manifest() -> dict:
    path = PROJECT_ROOT / "manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def load_project_info() -> dict:
    """Return project-level metadata + an estimated project_started timestamp."""
    import subprocess
    m = load_manifest()
    info: dict = {
        "name":            m.get("name", "cybersec"),
        "version":         m.get("version", "?"),
        "description":     m.get("description", ""),
        "project_started": None,
    }
    # 1 – git first-commit date (most accurate)
    try:
        r = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "log", "--reverse", "--format=%aI", "--max-count=1"],
            capture_output=True, text=True, timeout=3,
        )
        ts = r.stdout.strip()
        if r.returncode == 0 and ts:
            info["project_started"] = ts
    except Exception:  # noqa: BLE001
        pass
    # 2 – fallback: manifest.json mtime
    if not info["project_started"]:
        p = PROJECT_ROOT / "manifest.json"
        if p.exists():
            info["project_started"] = datetime.fromtimestamp(
                p.stat().st_mtime, tz=timezone.utc
            ).isoformat()
    return info


def load_recent_sessions(limit: int = 8) -> list[dict]:
    sessions_dir = PROJECT_ROOT / "cybersec-sessions"
    if not sessions_dir.exists():
        return []
    sessions = []
    try:
        entries = sorted(
            (d for d in sessions_dir.iterdir() if d.is_dir()),
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )
        for entry in entries[:limit]:
            manifest_path = entry / "meta" / "session-manifest.json"
            manifest = {}
            if manifest_path.exists():
                try:
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    pass
            ioc_count = 0
            ioc_file = entry / "iocs.md"
            if ioc_file.exists():
                try:
                    ioc_count = sum(1 for ln in ioc_file.read_text().splitlines() if ln.startswith("|"))
                except OSError:
                    pass
            sessions.append({
                "id":             entry.name,
                "path":           str(entry),
                "mtime":          datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat(),
                "ioc_count":      ioc_count,
                "manifest":       manifest,
                # convenience fields surfaced directly from session-manifest.json
                "start_time":     manifest.get("start_time"),
                "phase":          manifest.get("phase"),
                "status":         manifest.get("status"),
                "hostname":       manifest.get("hostname"),
                "investigator":   manifest.get("investigator"),
                "findings_count": manifest.get("findings_count", 0),
            })
    except OSError:
        pass
    return sessions


def load_last_sync_times() -> dict:
    meta_dir = PROJECT_ROOT / "data" / "cybersec-shared" / "meta"
    result = {}
    for fname, key in [
        ("last-intel-update.txt", "last_intel_update"),
        ("last-comprehensive-sync.txt", "last_comprehensive_sync"),
    ]:
        p = meta_dir / fname
        if p.exists():
            try:
                result[key] = p.read_text().strip()
            except OSError:
                pass
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Skills & agents data
# ──────────────────────────────────────────────────────────────────────────────

def _parse_frontmatter(text: str) -> dict:
    """Parse simple YAML frontmatter (--- delimited). Handles > block scalars."""
    if not text.startswith("---"):
        return {}
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}
    block = text[3:end].strip()
    result: dict = {}
    key = ""
    collecting_block = False
    block_lines: list[str] = []
    for line in block.splitlines():
        if collecting_block:
            if line.startswith("  ") or line.startswith("\t"):
                block_lines.append(line.strip())
                continue
            else:
                result[key] = " ".join(block_lines).strip()
                collecting_block = False
                block_lines = []
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            key = k.strip()
            v = v.strip()
            if v == ">":
                collecting_block = True
                block_lines = []
            else:
                result[key] = v.strip('"').strip("'")
    if collecting_block and block_lines:
        result[key] = " ".join(block_lines).strip()
    return result


def load_skills_data() -> dict:
    """Collect agent definitions, subagents, teams and hook registry."""
    agents_dir = PROJECT_ROOT / "agents"

    def _read_agents(path: Path) -> list[dict]:
        out = []
        if not path.exists():
            return out
        for f in sorted(path.glob("*.md")):
            try:
                meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
                out.append({
                    "name":        meta.get("name", f.stem),
                    "description": meta.get("description", ""),
                    "model":       meta.get("model", ""),
                    "color":       meta.get("color", "gray"),
                    "role":        meta.get("role", ""),
                    "max_turns":   meta.get("maxTurns", ""),
                    "tools":       meta.get("tools", ""),
                    "file":        f.name,
                })
            except OSError:
                pass
        return out

    # hooks.json
    hooks: dict = {}
    hooks_path = PROJECT_ROOT / "hooks" / "hooks.json"
    if hooks_path.exists():
        try:
            hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass

    return {
        "skills":       load_settings().get("skills", {}),
        "main_agents":  _read_agents(agents_dir),
        "subagents":    _read_agents(agents_dir / "subagents"),
        "teams":        _read_agents(agents_dir / "teams"),
        "hooks":        hooks,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Certificate data
# ──────────────────────────────────────────────────────────────────────────────

CERTS_DIR = PROJECT_ROOT / ".certs"
CERT_TARGETS = ["postgres", "mcp", "dashboard"]


def _read_cert_info(cert_path: Path) -> dict:
    """Run openssl x509 to extract metadata from a PEM cert file."""
    info: dict = {
        "subject": "", "issuer": "", "not_before": "", "not_after": "",
        "fingerprint": "", "is_expired": False, "days_until_expiry": None,
        "san": "",
    }
    if not cert_path.exists():
        return info
    try:
        r = subprocess.run(
            ["openssl", "x509", "-in", str(cert_path), "-noout",
             "-subject", "-issuer", "-dates", "-fingerprint", "-sha256",
             "-ext", "subjectAltName"],
            capture_output=True, text=True, timeout=5,
        )
        for line in r.stdout.splitlines():
            if line.startswith("subject="):
                info["subject"] = line[8:]
            elif line.startswith("issuer="):
                info["issuer"] = line[7:]
            elif line.startswith("notAfter="):
                na = line[9:].strip()
                info["not_after"] = na
                try:
                    exp = datetime.strptime(na, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                    days = (exp - datetime.now(tz=timezone.utc)).days
                    info["days_until_expiry"] = days
                    info["is_expired"] = days < 0
                except ValueError:
                    pass
            elif line.startswith("notBefore="):
                info["not_before"] = line[10:].strip()
            elif "Fingerprint=" in line:
                info["fingerprint"] = line.split("=", 1)[1].strip()
            elif "DNS:" in line or "IP:" in line:
                info["san"] = line.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return info


def load_certs_data(msg: str = "") -> dict:
    """Scan .certs/ directory and return status for all targets."""
    result: dict = {"msg": msg, "targets": {}}

    ca_cert = CERTS_DIR / "ca" / "ca.crt"
    ca_key  = CERTS_DIR / "ca" / "ca.key"
    result["ca"] = {
        "has_cert": ca_cert.exists(),
        "has_key":  ca_key.exists(),
        "cert_path": str(ca_cert),
        "info": _read_cert_info(ca_cert),
    }

    for t in CERT_TARGETS:
        td = CERTS_DIR / t
        sc = td / "server.crt"
        sk = td / "server.key"
        cc = td / "client.crt"   # postgres client cert
        ck = td / "client.key"
        result["targets"][t] = {
            "has_cert":        sc.exists(),
            "has_key":         sk.exists(),
            "has_client_cert": cc.exists(),
            "cert_path":       str(sc),
            "key_path":        str(sk),
            "info":            _read_cert_info(sc),
        }
    return result


def generate_cert_for_target(target: str) -> str:
    """Generate a CA-signed TLS certificate for target. Returns status message."""
    import tempfile, os as _os

    ca_dir  = CERTS_DIR / "ca"
    tgt_dir = CERTS_DIR / target
    ca_dir.mkdir(parents=True, exist_ok=True)
    tgt_dir.mkdir(parents=True, exist_ok=True)

    ca_key  = ca_dir / "ca.key"
    ca_cert = ca_dir / "ca.crt"

    # ── 1. Create CA if absent ────────────────────────────────────────────────
    if not ca_cert.exists():
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096", "-days", "3650",
            "-nodes", "-subj", "/CN=CyberSec-CA/O=CyberSec/C=DE",
            "-keyout", str(ca_key), "-out", str(ca_cert),
        ], check=True, timeout=30, capture_output=True)

    # ── 2. Determine CN + SANs ────────────────────────────────────────────────
    CN_MAP = {
        "postgres":  ("cybersec-postgres", "DNS:cybersec-postgres,DNS:localhost,IP:127.0.0.1"),
        "mcp":       ("localhost",          "DNS:localhost,IP:127.0.0.1"),
        "dashboard": ("localhost",          "DNS:localhost,IP:127.0.0.1"),
    }
    cn, san = CN_MAP.get(target, (target, f"DNS:{target},DNS:localhost"))

    srv_key = tgt_dir / "server.key"
    srv_csr = tgt_dir / "server.csr"
    srv_crt = tgt_dir / "server.crt"

    # ── 3. Generate key + CSR ─────────────────────────────────────────────────
    subprocess.run([
        "openssl", "req", "-newkey", "rsa:2048", "-nodes",
        "-subj", f"/CN={cn}/O=CyberSec/C=DE",
        "-keyout", str(srv_key), "-out", str(srv_csr),
    ], check=True, timeout=20, capture_output=True)

    # ── 4. Write SAN extension to temp file, sign ─────────────────────────────
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ext", delete=False) as tf:
        tf.write(f"subjectAltName={san}\n")
        ext_file = tf.name
    try:
        subprocess.run([
            "openssl", "x509", "-req", "-days", "825",
            "-in", str(srv_csr),
            "-CA", str(ca_cert), "-CAkey", str(ca_key), "-CAcreateserial",
            "-extfile", ext_file,
            "-out", str(srv_crt),
        ], check=True, timeout=20, capture_output=True)
    finally:
        _os.unlink(ext_file)
        srv_csr.unlink(missing_ok=True)

    # ── 5. For postgres: also generate client cert ────────────────────────────
    if target == "postgres":
        cl_key = tgt_dir / "client.key"
        cl_csr = tgt_dir / "client.csr"
        cl_crt = tgt_dir / "client.crt"
        subprocess.run([
            "openssl", "req", "-newkey", "rsa:2048", "-nodes",
            "-subj", "/CN=cybersec/O=CyberSec/C=DE",
            "-keyout", str(cl_key), "-out", str(cl_csr),
        ], check=True, timeout=20, capture_output=True)
        subprocess.run([
            "openssl", "x509", "-req", "-days", "825",
            "-in", str(cl_csr),
            "-CA", str(ca_cert), "-CAkey", str(ca_key), "-CAcreateserial",
            "-out", str(cl_crt),
        ], check=True, timeout=20, capture_output=True)
        cl_csr.unlink(missing_ok=True)

    return f"✓ Certificate generated for '{target}' → {srv_crt}"


def save_cert_from_pem(target: str, cert_pem: str, key_pem: str) -> str:
    """Save user-supplied PEM content for a target. Returns status message."""
    if target not in CERT_TARGETS:
        return f"✗ Unknown target '{target}'"
    tgt_dir = CERTS_DIR / target
    tgt_dir.mkdir(parents=True, exist_ok=True)
    if cert_pem.strip():
        (tgt_dir / "server.crt").write_text(cert_pem.strip() + "\n", encoding="utf-8")
    if key_pem.strip():
        (tgt_dir / "server.key").write_text(key_pem.strip() + "\n", encoding="utf-8")
        (tgt_dir / "server.key").chmod(0o600)
    return f"✓ Custom certificate saved for '{target}'"


async def collect_db_data() -> dict:
    """Try to connect and collect health + counts. Always closes Tortoise when done."""
    db: dict = {
        "status": "error",
        "error": None,
        "postgresql_version": None,
        "table_count": 0,
        "tables": [],
        "counts": {},
        "initialized": False,
        "intel_bootstrapped": False,
        "config": {},
    }
    try:
        # Force-reset any stale Tortoise state from a previous event loop
        # (important when called repeatedly from the --serve request handler)
        from db import bootstrap as _bs
        _bs._initialized = False
        _bs._intel_bootstrapped = False

        from db.bootstrap import get_database_health_async
        health = await get_database_health_async(
            check_connection=True,
            include_counts=True,
            create_db=False,
            bootstrap_intel=False,
        )
        db["status"] = health.get("status", "error")
        db["error"] = health.get("error")
        db["initialized"] = health.get("initialized", False)
        db["intel_bootstrapped"] = health.get("intel_bootstrapped", False)
        db["config"] = health.get("config", {})
        db["table_count"] = health.get("table_count", 0)
        db["tables"] = health.get("tables", [])
        db["counts"] = health.get("counts", {})
        raw_ver = health.get("database_version") or ""
        db["postgresql_version"] = raw_ver.split(",")[0].strip() if raw_ver else None
    except Exception as exc:  # noqa: BLE001
        db["error"] = str(exc)
    finally:
        # Always release connections so the next call gets a clean event loop
        try:
            from db.bootstrap import close_tortoise
            await close_tortoise()
        except Exception:  # noqa: BLE001
            pass
    return db


def collect_all_data() -> dict:
    settings  = load_settings()
    manifest  = load_manifest()
    project   = load_project_info()
    sessions  = load_recent_sessions()
    sync_times = load_last_sync_times()
    db = asyncio.run(collect_db_data())
    return {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "mode":         settings.get("mode", "unknown"),
        "settings":     settings,
        "manifest":     manifest,
        "project":      project,
        "sessions":     sessions,
        "sync_times":   sync_times,
        "db":           db,
    }


# ──────────────────────────────────────────────────────────────────────────────
# HTML generation
# ──────────────────────────────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{refresh_tag}
<title>CyberSec Dashboard</title>
<style>
:root {
  /* ── Neutral Dark Grey ──────────────────────────────────────────────── */
  --bg:       #0d0d0d;
  --surface:  #141414;
  --surface2: #1f1f1f;
  --border:   #2d2d2d;
  --text:     #e2e2e2;
  --subtext:  #999999;
  --muted:    #555555;
  --ok:       #59b87a;
  --err:      #cc5c5c;
  --warn:     #c0923a;
  --accent:   #ACCENT_COLOR;
  --accent2:  #ACCENT2_COLOR;
  --font:     "Fira Code","Cascadia Code","Consolas",monospace;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 14px; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  min-height: 100vh;
  padding: 0 0 2rem;
}

/* ── Header ── */
header {
  background: linear-gradient(135deg, var(--surface) 0%, #080808 100%);
  border-bottom: 1px solid var(--border);
  padding: 1.1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: sticky;
  top: 0;
  z-index: 100;
}
.logo {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: .05em;
  color: var(--accent);
  text-shadow: 0 0 18px var(--accent);
}
.mode-badge {
  padding: .2rem .7rem;
  border-radius: 9999px;
  font-size: .75rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  background: color-mix(in srgb, var(--accent) 15%, transparent);
  color: var(--accent);
  border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent);
}
.header-right { margin-left: auto; display: flex; align-items: center; gap: .9rem; font-size: .7rem; color: var(--muted); }
.clock {
  font-size: .82rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: .08em;
  font-variant-numeric: tabular-nums;
  min-width: 6.5ch;
  text-align: right;
}
.db-pill {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  padding: .15rem .6rem;
  border-radius: 9999px;
  font-size: .7rem;
  font-weight: 600;
}
.db-pill.ok  { background: color-mix(in srgb, var(--ok)  15%, transparent); color: var(--ok);  border: 1px solid color-mix(in srgb, var(--ok)  35%, transparent); }
.db-pill.err { background: color-mix(in srgb, var(--err) 15%, transparent); color: var(--err); border: 1px solid color-mix(in srgb, var(--err) 35%, transparent); }
.dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.dot.pulse { animation: pulse 2s infinite; }
@keyframes pulse {
  0%,100% { opacity: 1; }
  50%      { opacity: .35; }
}

/* ── Grid ── */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 1.1rem;
  display: flex;
  flex-direction: column;
  gap: .6rem;
}
.card.wide { grid-column: span 2; }
.card-title {
  font-size: .65rem;
  font-weight: 700;
  letter-spacing: .15em;
  text-transform: uppercase;
  color: var(--accent);
  border-bottom: 1px solid var(--border);
  padding-bottom: .45rem;
  margin-bottom: .1rem;
}
.kv { display: flex; justify-content: space-between; align-items: center; font-size: .78rem; padding: .15rem 0; }
.kv-key  { color: var(--muted); }
.kv-val  { color: var(--text); font-weight: 600; text-align: right; max-width: 55%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.kv-val.ok   { color: var(--ok); }
.kv-val.err  { color: var(--err); }
.kv-val.warn { color: var(--warn); }

/* ── Counts table ── */
.counts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(145px, 1fr));
  gap: .5rem;
}
.count-cell {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: .55rem .65rem;
  display: flex;
  flex-direction: column;
  gap: .2rem;
}
.count-label { font-size: .6rem; color: var(--muted); letter-spacing: .08em; text-transform: uppercase; }
.count-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--accent);
  line-height: 1;
}
.count-value.zero { color: var(--muted); font-size: 1.1rem; }

/* ── Table list ── */
.table-list {
  display: flex;
  flex-wrap: wrap;
  gap: .3rem;
}
.table-tag {
  font-size: .65rem;
  padding: .15rem .45rem;
  border-radius: 4px;
  background: color-mix(in srgb, var(--accent) 8%, transparent);
  color: color-mix(in srgb, var(--accent) 70%, var(--text));
  border: 1px solid color-mix(in srgb, var(--accent) 18%, transparent);
}

/* ── Sessions ── */
.session-row {
  font-size: .72rem;
  padding: .45rem 0;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: .25rem;
}
.session-row:last-child { border-bottom: none; }
.session-top { display: flex; align-items: center; gap: .5rem; }
.session-id   { color: var(--accent); font-weight: 600; flex: 1; }
.session-meta { color: var(--muted); font-size: .65rem; margin-left: auto; white-space: nowrap; }
.session-detail {
  display: flex; flex-wrap: wrap; gap: .3rem;
  font-size: .63rem; color: var(--subtext);
}
.session-badge {
  padding: .1rem .4rem;
  border-radius: 4px;
  border: 1px solid var(--border);
  background: var(--surface2);
  white-space: nowrap;
}
.session-badge.active { color: var(--ok);   border-color: color-mix(in srgb, var(--ok)  30%, transparent); background: color-mix(in srgb, var(--ok)  8%, transparent); }
.session-badge.ended  { color: var(--muted); }
.session-badge.phase  { color: var(--accent2); border-color: color-mix(in srgb, var(--accent2) 30%, transparent); }

/* ── Flags ── */
.flag {
  display: inline-flex;
  align-items: center;
  gap: .25rem;
  font-size: .68rem;
  padding: .12rem .45rem;
  border-radius: 4px;
}
.flag.on  { background: color-mix(in srgb, var(--ok)  12%, transparent); color: var(--ok);   border: 1px solid color-mix(in srgb, var(--ok)  25%, transparent); }
.flag.off { background: color-mix(in srgb, var(--err)  8%, transparent); color: var(--muted); border: 1px solid color-mix(in srgb, var(--err) 15%, transparent); }

/* ── Error box ── */
.error-box {
  font-size: .7rem;
  color: var(--err);
  background: color-mix(in srgb, var(--err) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--err) 30%, transparent);
  border-radius: 6px;
  padding: .5rem .7rem;
  word-break: break-all;
}
.phases { display: flex; flex-wrap: wrap; gap: .25rem; }
.phase-tag {
  font-size: .62rem;
  padding: .12rem .4rem;
  border-radius: 4px;
  background: color-mix(in srgb, var(--border) 80%, transparent);
  color: var(--muted);
  border: 1px solid var(--border);
}

footer {
  text-align: center;
  font-size: .62rem;
  color: var(--muted);
  padding: 1rem 1.5rem 0;
}

/* ── Page navigation ── */
.page-nav { display: flex; gap: .3rem; margin-left: .8rem; }
.nav-link {
  font-size: .7rem; font-weight: 600; letter-spacing: .05em;
  padding: .22rem .6rem; border-radius: 5px;
  text-decoration: none; color: var(--muted);
  border: 1px solid transparent;
  transition: color .15s, border-color .15s, background .15s;
}
.nav-link:hover { color: var(--subtext); border-color: var(--border); }
.nav-active {
  color: var(--accent) !important;
  border-color: color-mix(in srgb, var(--accent) 35%, transparent) !important;
  background: color-mix(in srgb, var(--accent) 9%, transparent);
}
/* ── Sub-page cards (skills/certs) ── */
.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: .7rem;
}
.agent-card {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: .75rem .9rem;
  display: flex; flex-direction: column; gap: .35rem;
}
.agent-name { font-size: .78rem; font-weight: 700; }
.agent-desc { font-size: .65rem; color: var(--subtext); line-height: 1.45; }
.agent-meta { display: flex; flex-wrap: wrap; gap: .25rem; margin-top: .15rem; }
.badge {
  font-size: .6rem; padding: .1rem .4rem; border-radius: 4px;
  border: 1px solid var(--border); background: var(--surface);
  color: var(--muted);
}
.badge.color-green  { color:#59b87a; border-color:color-mix(in srgb,#59b87a 30%,transparent); background:color-mix(in srgb,#59b87a 8%,transparent); }
.badge.color-yellow { color:#c0923a; border-color:color-mix(in srgb,#c0923a 30%,transparent); background:color-mix(in srgb,#c0923a 8%,transparent); }
.badge.color-red    { color:#cc5c5c; border-color:color-mix(in srgb,#cc5c5c 30%,transparent); background:color-mix(in srgb,#cc5c5c 8%,transparent); }
.badge.color-blue   { color:#6a9fbf; border-color:color-mix(in srgb,#6a9fbf 30%,transparent); background:color-mix(in srgb,#6a9fbf 8%,transparent); }
.badge.color-purple { color:#9272b0; border-color:color-mix(in srgb,#9272b0 30%,transparent); background:color-mix(in srgb,#9272b0 8%,transparent); }
.badge.color-cyan   { color:#5abccc; border-color:color-mix(in srgb,#5abccc 30%,transparent); background:color-mix(in srgb,#5abccc 8%,transparent); }
.badge.color-gray   { color:var(--subtext); }
.badge.color-orange { color:#c0923a; border-color:color-mix(in srgb,#c0923a 30%,transparent); background:color-mix(in srgb,#c0923a 8%,transparent); }
/* cert page */
.cert-status {
  font-size:.7rem; padding:.55rem .75rem;
  border-radius:7px; margin-bottom:.4rem;
}
.cert-ok    { background:color-mix(in srgb,var(--ok)  10%,transparent); color:var(--ok);   border:1px solid color-mix(in srgb,var(--ok)  25%,transparent); }
.cert-warn  { background:color-mix(in srgb,var(--warn) 10%,transparent); color:var(--warn); border:1px solid color-mix(in srgb,var(--warn) 25%,transparent); }
.cert-miss  { background:color-mix(in srgb,var(--err)  8%,transparent);  color:var(--muted); border:1px solid color-mix(in srgb,var(--err) 20%,transparent); }
.cert-btn {
  display:inline-block; font-size:.7rem; font-weight:600; letter-spacing:.05em;
  padding:.3rem .85rem; border-radius:5px; border:none; cursor:pointer;
  background:color-mix(in srgb,var(--accent) 15%,transparent);
  color:var(--accent);
  border:1px solid color-mix(in srgb,var(--accent) 30%,transparent);
  transition:background .15s;
}
.cert-btn:hover { background:color-mix(in srgb,var(--accent) 25%,transparent); }
.cert-btn.secondary { background:var(--surface2); color:var(--subtext); border-color:var(--border); }
textarea.pem-input {
  width:100%; height:7rem; background:var(--surface); color:var(--text);
  border:1px solid var(--border); border-radius:5px;
  font-family:var(--font); font-size:.63rem; padding:.4rem .5rem;
  resize:vertical; margin-top:.3rem;
}
.msg-box {
  font-size:.72rem; padding:.5rem .9rem; border-radius:6px; margin-bottom:.75rem;
  background:color-mix(in srgb,var(--ok) 10%,transparent);
  color:var(--ok); border:1px solid color-mix(in srgb,var(--ok) 25%,transparent);
}
.msg-box.err { background:color-mix(in srgb,var(--err) 10%,transparent); color:var(--err); border-color:color-mix(in srgb,var(--err) 25%,transparent); }
details > summary { cursor:pointer; color:var(--muted); font-size:.68rem; margin-top:.3rem; }
details > summary:hover { color:var(--subtext); }
details[open] > summary { color:var(--accent); }
</style>
</head>
<body>
<header>
  <span class="logo">⬡ CyberSec</span>
  <span class="mode-badge" id="modeBadge"></span>
  <span class="db-pill" id="dbPill">
    <span class="dot pulse" id="dbDot"></span>
    <span id="dbLabel"></span>
  </span>
  <span class="header-right">
    <span id="genLabel"></span>
    <span class="clock" id="clock"></span>
  </span>
</header>

<div class="grid" id="grid"></div>

<footer id="footer"></footer>

<script>
const DATA = __DATA_PLACEHOLDER__;

// ── Helpers ──────────────────────────────────────────────────────────────────
const el = (tag, cls, html) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html !== undefined) e.innerHTML = html;
  return e;
};
const fmt = n => n == null ? '—' : Number(n).toLocaleString();
const fmtDate = iso => {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString(undefined, {
      month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'
    });
  } catch { return iso; }
};

// ── Mode colours (muted, grey-tinted) ────────────────────────────────────────
const MODE_META = {
  blue:   { label: '🔵 Blue Team',   accent: '#6a9fbf', accent2: '#527d99' },
  red:    { label: '🔴 Red Team',    accent: '#bf6a6a', accent2: '#995252' },
  purple: { label: '🟣 Purple Team', accent: '#9272b0', accent2: '#745a91' },
};
const mode = (DATA.mode || 'blue').toLowerCase();
const meta = MODE_META[mode] || MODE_META.blue;

// Apply accent colours
document.documentElement.style.setProperty('--accent',  meta.accent);
document.documentElement.style.setProperty('--accent2', meta.accent2);

// ── Header ───────────────────────────────────────────────────────────────────
document.getElementById('modeBadge').textContent = meta.label;

const db = DATA.db || {};
const dbOk = db.status === 'ok';
const pill = document.getElementById('dbPill');
const dot  = document.getElementById('dbDot');
pill.classList.add(dbOk ? 'ok' : 'err');
dot.classList.toggle('pulse', dbOk);
document.getElementById('dbLabel').textContent = dbOk ? 'DB Connected' : 'DB Offline';

document.getElementById('genLabel').textContent =
  'Generated ' + fmtDate(DATA.generated_at);

// ── Live clock ───────────────────────────────────────────────────────────────
(function tickClock() {
  const clockEl = document.getElementById('clock');
  function tick() {
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    const ss = String(now.getSeconds()).padStart(2, '0');
    clockEl.textContent = `${hh}:${mm}:${ss}`;
  }
  tick();
  setInterval(tick, 1000);
})();

// ── Card builder ─────────────────────────────────────────────────────────────
const grid = document.getElementById('grid');

function card(title, buildFn, wide = false) {
  const c = el('div', 'card' + (wide ? ' wide' : ''));
  c.appendChild(el('div', 'card-title', title));
  buildFn(c);
  grid.appendChild(c);
}

function kv(parent, key, value, cls = '') {
  const row = el('div', 'kv');
  row.appendChild(el('span', 'kv-key', key));
  const v = el('span', 'kv-val' + (cls ? ' ' + cls : ''), String(value ?? '—'));
  row.appendChild(v);
  parent.appendChild(row);
}

function flag(parent, label, on) {
  const f = el('span', 'flag ' + (on ? 'on' : 'off'), (on ? '✓ ' : '✗ ') + label);
  parent.appendChild(f);
}

// ── Card 0: Project Info ─────────────────────────────────────────────────────
card('Project Info', c => {
  const p = DATA.project || {};
  const s = DATA.settings || {};
  kv(c, 'Name',           p.name    || '—');
  kv(c, 'Version',        p.version || '—');
  kv(c, 'Agent',          s['agent:'] || '—');
  kv(c, 'Project Started', fmtDate(p.project_started) || '—');

  // most recent session start
  const sessions = DATA.sessions || [];
  const latest = sessions.find(s => s.start_time) || sessions[0];
  if (latest) {
    kv(c, 'Last Session Started', fmtDate(latest.start_time || latest.mtime) || '—');
    if (latest.hostname)
      kv(c, 'Host', latest.hostname);
    if (latest.investigator)
      kv(c, 'Investigator', latest.investigator);
  }

  if (p.description) {
    const desc = document.createElement('div');
    desc.style.cssText = 'font-size:.67rem;color:var(--subtext);margin-top:.35rem;line-height:1.5;';
    desc.textContent = p.description.length > 160
      ? p.description.slice(0, 157) + '…'
      : p.description;
    c.appendChild(desc);
  }
});

// ── Card 1: DB Status ────────────────────────────────────────────────────────
card('Database Status', c => {
  const cfg = db.config || {};
  const isSocket = (cfg.host || '').startsWith('/');
  const hostLabel = isSocket ? cfg.host : `${cfg.host || '—'}:${cfg.port || 5432}`;
  kv(c, 'Status',       dbOk ? 'Connected' : 'Offline',  dbOk ? 'ok' : 'err');
  if (db.postgresql_version)
    kv(c, 'PostgreSQL',   db.postgresql_version);
  kv(c, isSocket ? 'Socket' : 'Host', hostLabel);
  kv(c, 'Database',     cfg.database || '—');
  kv(c, 'User',         cfg.user || '—');
  kv(c, 'Tables',       fmt(db.table_count));
  kv(c, 'Initialized',  db.initialized  ? 'Yes' : 'No',  db.initialized  ? 'ok' : 'warn');
  kv(c, 'Intel Seeded', db.intel_bootstrapped ? 'Yes' : 'No',
                        db.intel_bootstrapped ? 'ok' : 'warn');
  if (db.error) {
    const box = el('div', 'error-box', '⚠ ' + db.error);
    c.appendChild(box);
  }
});

// ── Card 2: Intel Counts ─────────────────────────────────────────────────────
card('Intelligence Counts', c => {
  const counts = db.counts || {};
  const LABELS = {
    intel_cves:                    'CVEs',
    intel_cwes:                    'CWEs',
    intel_capec_patterns:          'CAPEC',
    intel_mitre_techniques:        'MITRE Techniques',
    intel_mitre_threat_actors:     'Threat Actors',
    intel_mitre_software_families: 'Software Families',
    intel_feed_snapshots:          'Feed Snapshots',
    intel_misp_events:             'MISP Events',
    intel_misp_attributes:         'MISP Attributes',
    intel_opencti_indicators:      'OpenCTI Indicators',
    intel_opencti_entities:        'OpenCTI Entities',
  };
  const cg = el('div', 'counts-grid');
  for (const [key, label] of Object.entries(LABELS)) {
    const val = counts[key] ?? 0;
    const cell = el('div', 'count-cell');
    cell.appendChild(el('span', 'count-label', label));
    cell.appendChild(el('span', 'count-value' + (val === 0 ? ' zero' : ''), fmt(val)));
    cg.appendChild(cell);
  }
  c.appendChild(cg);
}, true);

// ── Card 3: DB Tables ────────────────────────────────────────────────────────
card('DB Tables (' + fmt(db.table_count) + ')', c => {
  const tables = db.tables || [];
  if (tables.length === 0) {
    c.appendChild(el('span', 'kv-key', 'No tables — schema not yet created'));
    return;
  }
  const tl = el('div', 'table-list');
  tables.forEach(t => tl.appendChild(el('span', 'table-tag', t)));
  c.appendChild(tl);
}, true);

// ── Card 4: Active Mode ───────────────────────────────────────────────────────
card('Active Mode', c => {
  const s = DATA.settings || {};
  const modeKey = (s.mode || 'blue') + '_team';
  const modeConf = s[modeKey] || {};

  kv(c, 'Mode', (s.mode || '—').toUpperCase());
  kv(c, 'Agent', s['agent:'] || '—');

  const flags = el('div', 'phases');
  const bool_keys = [
    ['enable_threat_hunting',    'Threat Hunting'],
    ['enable_incident_response', 'Incident Response'],
    ['enable_forensic_analysis', 'Forensic Analysis'],
    ['defensive_analysis',       'Defensive Analysis'],
    ['ioc_enrichment',           'IOC Enrichment'],
  ];
  bool_keys.forEach(([k, label]) => {
    if (k in modeConf) flag(flags, label, modeConf[k]);
  });
  if (flags.children.length) c.appendChild(flags);

  if (Array.isArray(modeConf.focus_areas) && modeConf.focus_areas.length) {
    const fa = el('div', 'phases');
    modeConf.focus_areas.forEach(a => fa.appendChild(el('span', 'phase-tag', a.replace(/_/g,' '))));
    c.appendChild(el('div', 'kv-key', 'Focus Areas'));
    c.appendChild(fa);
  }
});

// ── Card 5: Agent Settings ───────────────────────────────────────────────────
card('Agent Settings', c => {
  const a = (DATA.settings || {}).agents || {};
  kv(c, 'Default Model',     a.default_model || '—');
  kv(c, 'Elite Model',       a.elite_model   || '—');
  kv(c, 'Cross-Val Sources', a.cross_validation_min_sources ?? '—');

  const flags = el('div', 'phases');
  [
    ['non_destructive',     'Non-Destructive'],
    ['require_ioc_logging', 'IOC Logging'],
    ['require_mitre_mapping','MITRE Mapping'],
    ['offensive_techniques', 'Offensive Tech'],
    ['exploit_suggestions',  'Exploit Hints'],
  ].forEach(([k, label]) => {
    if (k in a) flag(flags, label, a[k]);
  });
  c.appendChild(flags);
});

// ── Card 6: Phases ───────────────────────────────────────────────────────────
card('Investigation Phases', c => {
  const phases = (DATA.settings || {}).phases || [];
  if (!phases.length) {
    c.appendChild(el('span', 'kv-key', 'No phases configured'));
    return;
  }
  const pg = el('div', 'phases');
  phases.forEach((p, i) => {
    const t = el('span', 'phase-tag', `${i + 1}. ${p}`);
    pg.appendChild(t);
  });
  c.appendChild(pg);
});

// ── Card 7: Active Skills ────────────────────────────────────────────────────
card('Active Skills', c => {
  const skills = (DATA.settings || {}).skills || {};
  const entries = Object.entries(skills);
  if (!entries.length) {
    c.appendChild(el('span', 'kv-key', 'No skills configured'));
    return;
  }
  entries.forEach(([name, conf]) => {
    const on = conf && conf.enabled !== false;
    const auto = conf && conf.auto_activate;
    const row = el('div', 'kv');
    row.appendChild(el('span', 'kv-key', name));
    const right = el('span', '');
    right.style.display = 'flex';
    right.style.gap = '.3rem';
    flag(right, 'enabled',     on);
    if (auto !== undefined) flag(right, 'auto', auto);
    row.appendChild(right);
    c.appendChild(row);
  });
});

// ── Card 8: Recent Sessions ──────────────────────────────────────────────────
card('Recent Sessions', c => {
  const sessions = DATA.sessions || [];
  if (!sessions.length) {
    c.appendChild(el('span', 'kv-key', 'No sessions found in cybersec-sessions/'));
    return;
  }
  sessions.forEach(s => {
    const row = el('div', 'session-row');

    // top row: ID + IOC badge + timestamp
    const top = el('div', 'session-top');
    top.appendChild(el('span', 'session-id', s.id));
    if (s.ioc_count > 0)
      top.appendChild(el('span', 'flag on', `${s.ioc_count} IOCs`));
    top.appendChild(el('span', 'session-meta',
      'Started ' + fmtDate(s.start_time || s.mtime)));
    row.appendChild(top);

    // detail row: phase · status · hostname · findings
    const detail = el('div', 'session-detail');
    if (s.phase) {
      const b = el('span', 'session-badge phase', '⬡ ' + s.phase);
      detail.appendChild(b);
    }
    if (s.status) {
      const active = s.status === 'active';
      const b = el('span', 'session-badge ' + (active ? 'active' : 'ended'),
        active ? '● active' : '◎ ' + s.status);
      detail.appendChild(b);
    }
    if (s.hostname)
      detail.appendChild(el('span', 'session-badge', '🖥 ' + s.hostname));
    if (s.findings_count)
      detail.appendChild(el('span', 'session-badge', `⚑ ${s.findings_count} findings`));
    if (detail.children.length) row.appendChild(detail);

    c.appendChild(row);
  });
});

// ── Card 9: Sync Status ──────────────────────────────────────────────────────
card('Intel Sync Status', c => {
  const sync = DATA.sync_times || {};
  kv(c, 'Last Intel Update',    fmtDate(sync.last_intel_update)       || '—');
  kv(c, 'Last Weekly Sync',     fmtDate(sync.last_comprehensive_sync) || '—');

  const intelDir = PROJECT_ROOT + '/data/cybersec-shared/intelligence';
  kv(c, 'Intel Dir', 'data/cybersec-shared/intelligence');

  const cmds = el('div', 'phases');
  cmds.style.marginTop = '.35rem';
  [
    'python3 manage.py seed-intel',
    './scripts/update_threat_intel.sh',
    './scripts/weekly_intel_sync.sh',
  ].forEach(cmd => {
    const t = el('span', 'phase-tag', cmd);
    t.style.fontFamily = 'monospace';
    cmds.appendChild(t);
  });
  c.appendChild(el('div', 'kv-key', 'Sync Commands'));
  c.appendChild(cmds);
});

// ── Footer ───────────────────────────────────────────────────────────────────
document.getElementById('footer').textContent =
  'CyberSec v' + ((DATA.manifest || {}).version || '?') +
  ' · Generated ' + fmtDate(DATA.generated_at) +
  ' · skills/dashboard/generate_dashboard.py --serve for live updates';

</script>
</body>
</html>
"""


def render_html(data: dict, serve_refresh_secs: int | None = None) -> str:
    refresh_tag = (
        f'<meta http-equiv="refresh" content="{serve_refresh_secs}">'
        if serve_refresh_secs
        else ""
    )
    mode = (data.get("mode") or "blue").lower()
    from_mode = {
        "red":    ("#bf6a6a", "#995252"),
        "purple": ("#9272b0", "#745a91"),
    }
    accent, accent2 = from_mode.get(mode, ("#6a9fbf", "#527d99"))
    html = (
        HTML_TEMPLATE
        .replace("{refresh_tag}", refresh_tag)
        .replace("ACCENT_COLOR",  accent)
        .replace("ACCENT2_COLOR", accent2)
        .replace("__DATA_PLACEHOLDER__", json.dumps(data, default=str, ensure_ascii=False))
    )
    return html


def write_dashboard(data: dict, refresh_secs: int | None = None) -> Path:
    html = render_html(data, serve_refresh_secs=refresh_secs)
    OUT_FILE.write_text(html, encoding="utf-8")
    return OUT_FILE


# ──────────────────────────────────────────────────────────────────────────────
# HTTP server (--serve mode)
# ──────────────────────────────────────────────────────────────────────────────
AUTO_REFRESH_SECS = 10  # <meta http-equiv="refresh"> interval

def serve(port: int = 8322, host: str = "127.0.0.1") -> None:
    """HTTP server that regenerates the dashboard on every GET request.

    This avoids stale-data problems: each browser refresh hits the handler,
    which calls collect_all_data() fresh and returns up-to-date HTML.
    No background thread, no asyncio event-loop reuse issues.
    """
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from typing import Any

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            path = self.path.split("?")[0].rstrip("/") or "/"
            if path in ("/", "/index.html"):
                try:
                    data = collect_all_data()
                    html = render_html(data, serve_refresh_secs=AUTO_REFRESH_SECS)
                    body = html.encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
                    self.send_header("Pragma", "no-cache")
                    self.end_headers()
                    self.wfile.write(body)
                except (OSError, ValueError, RuntimeError) as exc:
                    err_html = (
                        f"<pre style='color:red;background:#111;padding:1em'>"
                        f"Dashboard error:\n{exc}</pre>"
                    ).encode()
                    self.send_response(500)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(err_html)))
                    self.end_headers()
                    self.wfile.write(err_html)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, fmt: str, *args: Any) -> None:  # suppress access log noise
            pass

    url = f"http://localhost:{port}/"
    print(f"  🌐  Serving at {url}  (data refreshed on every browser reload, auto every {AUTO_REFRESH_SECS}s)")
    print("  Press Ctrl+C to stop.\n")
    httpd = HTTPServer((host, port), Handler)  # type: ignore[arg-type]
    httpd.serve_forever()


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="CyberSec Dashboard Generator")
    parser.add_argument("--open",   action="store_true", help="Open in browser after generating")
    parser.add_argument("--serve",  action="store_true", help="Start live-refresh HTTP server")
    parser.add_argument("--port",   type=int, default=8322, help="Port for --serve (default: 8765)")
    args = parser.parse_args()

    print("🔍 CyberSec Dashboard Generator")
    print(f"   Collecting data from {PROJECT_ROOT} …", flush=True)

    data = collect_all_data()

    db = data.get("db", {})
    mode = data.get("mode", "?")
    db_status = "✓ connected" if db.get("status") == "ok" else f"✗ offline ({db.get('error', '')})"
    tables = db.get("table_count", 0)
    total_intel = sum(int(v) for v in (db.get("counts") or {}).values())

    print(f"   Mode:     {mode.upper()}")
    print(f"   DB:       {db_status}")
    print(f"   Tables:   {tables}")
    print(f"   Intel:    {total_intel:,} total rows")

    if args.serve:
        # In serve mode we write an initial file so --open has something to load,
        # but the live server regenerates data on every request.
        out = write_dashboard(data, refresh_secs=10)
        print(f"\n✅ Initial snapshot written → {out}")
        url = f"http://localhost:{args.port}/"
        if args.open:
            import webbrowser
            webbrowser.open(url)
        serve(port=args.port)  # blocks forever
    else:
        out = write_dashboard(data)
        print(f"\n✅ Dashboard written → {out}")
        if args.open:
            import webbrowser
            webbrowser.open(out.as_uri())
        else:
            print(f"   Open file:///{out}  in your browser, or run with --serve for live updates")


if __name__ == "__main__":
    main()

