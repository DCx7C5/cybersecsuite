---
name: kernel-capabilities-enum-detect
description: Linux capability enumeration, auditing, and abuse detection. Covers CAP_* flags, capability sets (effective/permitted/inheritable/ambient/bounding), container escapes via capabilities, and forensic detection of capability misuse.
domain: cybersecurity
subdomain: endpoint-forensics
tags:
- linux
- capabilities
- privilege-escalation
- kernel
- blue-team
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1548
- T1068
- T1611
nist_csf:
- PR.AC-04
- DE.CM-01
capec: []
---

# Linux Capabilities Enumeration & Detection

## Overview

Linux capabilities divide root privileges into discrete units (e.g., `CAP_NET_ADMIN`, `CAP_SYS_PTRACE`). Attackers abuse misconfigured capabilities to escalate privileges without needing SUID binaries or full root access. This skill covers enumeration, audit, and detection of capability abuse.

## When to Use

- When auditing binaries for unnecessary elevated capabilities
- When investigating container escapes or privilege escalation
- When implementing least-privilege on Linux endpoints
- When hunting for capability-based persistence or evasion

## Prerequisites

- `libcap2-bin` package (`getcap`, `setcap`, `capsh`)
- `pscap` from `libcap-ng-utils` for process capability audit

## Core Commands

### Enumerate File Capabilities
```bash
# Find all files with capabilities set (recursive)
getcap -r / 2>/dev/null

# Common dangerous capabilities
getcap -r / 2>/dev/null | grep -E "cap_setuid|cap_net_raw|cap_sys_ptrace|cap_sys_admin|cap_dac_override"
```

### Enumerate Process Capabilities
```bash
# Per-process capability sets
cat /proc/<PID>/status | grep -i cap

# Decode capability hex values
capsh --decode=0x0000003fffffffff

# All running processes with capabilities
pscap -a 2>/dev/null

# Check current shell capabilities
capsh --print
```

### Identify Dangerous Capability Combinations

| Capability | Abuse Vector |
|---|---|
| `CAP_SYS_PTRACE` | Inject shellcode into any process (T1055) |
| `CAP_SYS_ADMIN` | Mount namespaces, bypass seccomp, write cgroups |
| `CAP_NET_RAW` | Raw socket sniffing, ARP poisoning |
| `CAP_DAC_OVERRIDE` | Read/write any file regardless of permissions |
| `CAP_SETUID` | Change UID to 0 (full root escalation) |
| `CAP_CHOWN` | Change ownership of any file |
| `cap_sys_module` | Load kernel modules (rootkit installation) |

### Check for Capability Abuse Vectors
```bash
# Find SUID + capability combinations
find / -perm -4000 -o -perm -2000 2>/dev/null | xargs getcap 2>/dev/null

# Python with cap_setuid
python3 -c "import os; os.setuid(0); os.system('/bin/bash')"

# Check ambient capabilities in containers
grep CapAmb /proc/1/status
```

### Remove Dangerous Capabilities
```bash
# Remove all capabilities from a binary
setcap -r /usr/bin/python3

# Remove specific cap
setcap cap_net_raw-eip /usr/bin/ping
```

## Forensic Detection Workflow

1. Run `getcap -r /` and baseline legitimate capabilities
2. Compare against known-good: `diff baseline_caps.txt current_caps.txt`
3. Run `pscap -a` — look for user processes with `cap_sys_admin` or `cap_setuid`
4. Check container spawned processes: `cat /proc/1/status | grep Cap`
5. Correlate with `auditd` events for `setcap` system calls

## MITRE ATT&CK Mapping

| Finding | Technique |
|---|---|
| Binary with `cap_setuid+ep` | T1548.001 — Setuid and Setgid |
| Process with `cap_sys_ptrace` injecting shellcode | T1055 — Process Injection |
| Container with `cap_sys_admin` escaping namespace | T1611 — Escape to Host |

