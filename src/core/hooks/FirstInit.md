---
description: 'One-time bootstrap hook — initializes database, seeds defaults, registers localhost, captures kernel baseline.'
---

# FirstInit Hook – CyberSec Plugin

**Trigger:** Very first run of the cybersec plugin (via `hooks.json → FirstInit`)

**Idempotent:** Checks `~/.claude/cybersec/.initialized` marker — skips if already done.

## What this hook does

### Step 1 — Directory Structure
Creates `cybersec-mem/project/`, `cybersec-mem/session/`, `~/.claude/cybersec/`,
copies project templates.

### Step 2 — Database Bootstrap
- Initializes Tortoise ORM with `generate_schemas(safe=True)`
- Creates all tables: workspaces, projects, sessions, findings, iocs, risks,
  mitre_techniques, baselines, watchlist_items, shared_entries,
  ip_addresses, domains, hosts, host_ip_addresses, kernels, kernel_modules

### Step 3 — Seed Default Scope
- Creates `default` workspace (path = project root)
- Creates `system` workspace (global)
- Creates `default` project under default workspace

### Step 4 — Auto-Detect & Register Localhost
- Hostname via `socket.gethostname()`
- IP addresses (all non-loopback v4/v6)
- OS name + version from `/etc/os-release`
- Architecture via `platform.machine()`
- Registers as `Host(is_localhost=True, is_target=False)`
- Links detected IPs via M2M

### Step 5 — Capture Initial Kernel Baseline
- Kernel version (`uname -r`)
- Boot parameters (`/proc/cmdline`)
- Taint value + decoded reasons (`/proc/sys/kernel/tainted`)
- Module count cross-check (lsmod vs /proc/modules, delta)
- LSM status (AppArmor / SELinux / none)
- Sysctl security settings (ptrace_scope, kptr_restrict, bpf_disabled, etc.)

### Step 6 — Write Marker
Writes `~/.claude/cybersec/.initialized` with:
```json
{
  "initialized_at": "2026-04-05T12:00:00",
  "version": "4.0.0",
  "tables": 16,
  "localhost": {"hostname": "anonsys", "ips": ["10.0.0.5"], ...}
}
```

## Output (additionalContext)
Full init report with steps completed, errors (if any), localhost details, and table count.

## Re-running
Delete `~/.claude/cybersec/.initialized` to force re-init:
```bash
rm ~/.claude/cybersec/.initialized
```

**Must run before any other hook. Listed first in hooks.json.**

