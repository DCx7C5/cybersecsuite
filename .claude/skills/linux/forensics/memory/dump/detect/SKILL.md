---
name: forensics-memory-dump-detect
description: Memory forensics — analyze process memory maps for injection indicators (rwx, /tmp/ libs, deleted executables, anonymous mappings). Reads /proc/<pid>/maps directly; no kernel module required.
domain: cybersecurity
subdomain: memory-forensics
tags:
- memory
- injection
- process
- /proc
- linux
mitre_attack:
- T1055
- T1055.001
- T1055.012
- T1620
cve: []
cwe:
- CWE-119
nist_csf:
- DE.CM-4
capec:
- CAPEC-640
---
## Overview

Userspace memory forensics on Linux via `/proc/<pid>/maps`. Detects injection indicators: rwx memory regions, anonymous executable mappings, `/tmp/`-backed libs, and deleted executables still mapped in memory. No kernel module or elevated tool required beyond read access to `/proc`.

## Usage

```
Invoke when: suspicious process detected, post-exploitation suspected, or memory-resident malware suspected.
Options: --analyze (inspect maps), --target process|all, --pid <PID>
```

## Injection Indicators

| Pattern | Significance |
|---|---|
| `rwx` permissions | Shellcode or JIT-compiled payload |
| `/tmp/` path | Dropper injecting from temp |
| `deleted` in path | Executable deleted after load (fileless) |
| `anonymous` mapping | Anonymous mmap with execute — suspicious |

## Output

- `session_dir/artifacts/memory/` — map dumps per PID
- `session_dir/findings.md` — findings with severity, PID, and offending region
- Severity: medium for individual indicators; high if multiple indicators on same PID

## MITRE Coverage

| Technique | Description |
|---|---|
| T1055 | Process Injection |
| T1055.001 | Dynamic-link Library Injection |
| T1055.012 | Process Hollowing |
| T1620 | Reflective Code Loading |
