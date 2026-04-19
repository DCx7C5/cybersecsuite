---
name: hunting-apt-hunt-detect
description: APT Hunt — multi-vector threat detection across processes, network, browser, and filesystem on any Linux system. Runs quick or deep scans, auto-detects system config, logs findings + IOCs to session directory.
domain: cybersecurity
subdomain: threat-hunting
tags:
- apt
- threat-hunting
- process-analysis
- ioc
- linux
mitre_attack:
- T1057
- T1082
- T1049
- T1036
- T1055
cve: []
cwe: []
nist_csf:
- DE.CM-1
- DE.CM-4
capec:
- CAPEC-169
---
## Overview

Full APT hunt across all attack vectors on a Linux host. Checks suspicious processes (memory mappings, deleted executables, rwx regions), network connections (C2 beaconing, DNS anomalies, ARP spoofing), browser artifacts, and filesystem indicators. Writes findings + IOCs to `session_dir/findings.md`.

## Usage

```
Invoke when: initial triage, periodic threat sweep, or after an alert fires.
Target options: process | network | browser | all
Mode options: quick (live checks only) | deep (+ artifact collection)
```

## Checks

| Target | Indicators checked |
|---|---|
| process | rwx mappings, deleted executables, `/tmp/` libs, lsof anomalies |
| network | ARP table, open connections, DNS anomalies, unusual ports |
| browser | running browser processes, suspicious extensions |
| filesystem | SUID/SGID, world-writable, recently modified system files |

## Output

- `session_dir/findings.md` — timestamped finding entries with severity (critical/high/medium/low)
- `session_dir/artifacts/` — raw collection for deep mode
- Uses `config.get_config()` for tool paths and legitimate-service whitelist

## MITRE Coverage

| Technique | Description |
|---|---|
| T1057 | Process Discovery |
| T1082 | System Information Discovery |
| T1049 | System Network Connections Discovery |
| T1036 | Masquerading (deleted/renamed executables) |
| T1055 | Process Injection detection |
