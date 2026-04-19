---
name: test-config-detect
description: System configuration test for CyberSecSuite/MalwareHunter — auto-detects OS, available forensics tools (lsof, tcpdump, volatility, etc.), browser paths, and workspace directory. Prints compatibility report.
domain: cybersecurity
subdomain: ops
tags:
- config
- system-detection
- compatibility
- tools
- linux
mitre_attack: []
cve: []
cwe: []
nist_csf: []
capec: []
---
## Overview

Validates the host environment for CyberSecSuite forensic operations. Detects Linux distro, checks for required + optional tool availability, resolves browser profile paths, and verifies `MALWAREHUNTER_BASE_DIR` workspace. Use before first investigation or after system changes.

## Usage

```
Run test-config to confirm all forensic tools are discoverable before starting a hunt.
Set MALWAREHUNTER_BASE_DIR env var to override default workspace path ($HOME/MalwareHunter).
```

## Detected Items

| Category | Items checked |
|---|---|
| OS | distro, kernel version, architecture |
| Required tools | ip, ss, ps, lsof |
| Optional tools | tcpdump, volatility, tshark, yara, strings |
| Browsers | Brave, Chrome, Firefox profile paths |
| Workspace | MALWAREHUNTER_BASE_DIR existence + writability |

## Notes

- Output is human-readable summary — not machine-parseable
- Missing optional tools degrade hunt capability but do not block execution
- Each tool check uses `which` + version probe
