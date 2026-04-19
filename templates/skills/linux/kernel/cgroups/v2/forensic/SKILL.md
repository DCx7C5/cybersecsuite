---
name: kernel-cgroups-v2-forensic
description: Linux cgroups v2 forensic analysis — resource isolation inspection, container escape detection via cgroup release agents, and cgroup-based persistence hunting.
domain: cybersecurity
subdomain: endpoint-forensics
tags:
- linux
- cgroups
- container-escape
- kernel
- blue-team
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1611
- T1055
- T1543
nist_csf:
- DE.CM-01
- PR.PT-04
capec: []
---

# Linux cgroups v2 Forensic Analysis

## Overview

Control Groups (cgroups) manage resource allocation for process groups. Attackers exploit cgroup release agents for container escapes (CVE-2022-0492) and abuse cgroup namespaces to persist or evade detection. This skill covers forensic inspection of the unified cgroup v2 hierarchy.

## When to Use

- When investigating container escape attempts
- When auditing Kubernetes/Docker workloads for cgroup misconfigurations
- When hunting for cgroup release_agent persistence
- When analyzing resource usage anomalies that may indicate cryptomining

## Prerequisites

- Access to `/sys/fs/cgroup/` (cgroup v2 unified hierarchy)
- `systemd-cgls`, `systemctl`, `findmnt`

## Core Commands

### Enumerate cgroup Hierarchy
```bash
# Check cgroup version in use
mount | grep cgroup

# Full hierarchy tree
systemd-cgls

# Flat list of all cgroups
find /sys/fs/cgroup -name "cgroup.procs" | xargs -I{} sh -c 'echo "=== {} ==="; cat {}'
```

### Detect release_agent Abuse (CVE-2022-0492 Pattern)
```bash
# Check for writable release_agent files (v1 only, but check for presence)
find /sys/fs/cgroup -name "release_agent" 2>/dev/null

# In v2, check for notify_on_release misuse
find /sys/fs/cgroup -name "notify_on_release" -exec cat {} \; 2>/dev/null | grep -v "^0"

# Detect containers with CAP_SYS_ADMIN that can remount cgroup v1
grep -r "SYS_ADMIN" /etc/docker/ /etc/containerd/ 2>/dev/null
```

### Inspect Process-to-cgroup Mapping
```bash
# Map all PIDs to their cgroup path
for pid in $(ls /proc | grep '^[0-9]'); do
  echo "$pid: $(cat /proc/$pid/cgroup 2>/dev/null | head -1)"
done | grep -v "^$"

# Find processes NOT in a cgroup (possible escape)
awk -F: '{print $3}' /proc/*/cgroup 2>/dev/null | sort -u

# Specific PID cgroup membership
cat /proc/<PID>/cgroup
```

### Resource Anomaly Detection (Cryptomining)
```bash
# Find cgroups with excessive CPU usage
cat /sys/fs/cgroup/*/cpu.stat 2>/dev/null | grep usage_usec | sort -t= -k2 -rn | head -20

# Find cgroups with no memory limit (potential abuse)
find /sys/fs/cgroup -name "memory.max" -exec sh -c 'v=$(cat {}); [ "$v" = "max" ] && echo {}' \;
```

### Container Escape Detection
```bash
# Check if we're inside a container
cat /proc/1/cgroup | grep -q "docker\|kubepods\|containerd" && echo "CONTAINER DETECTED"

# Check for writable cgroup fs from inside container
mount | grep "cgroup" | grep -v "ro,"

# Detect release_agent write (forensic artifact)
grep "release_agent" /var/log/audit/audit.log 2>/dev/null
```

## Forensic Workflow

1. Enumerate all cgroups: `systemd-cgls > cgroup_snapshot.txt`
2. Identify orphaned PIDs (processes not in expected cgroup slice)
3. Check `release_agent` files for scripts — any non-empty file is suspicious
4. Correlate PIDs in unexpected cgroups with network connections
5. Map cgroup resource limits — unlimited memory + high CPU = cryptomining indicator

## MITRE ATT&CK Mapping

| Finding | Technique |
|---|---|
| `release_agent` with script payload | T1611 — Escape to Host |
| Process bypassing cgroup limits | T1055 — Process Injection |
| Service registered in cgroup without systemd unit | T1543.002 — Systemd Service |

