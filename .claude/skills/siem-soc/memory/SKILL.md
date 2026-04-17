---
name: memory
description: 'Uses Rekall memory forensics framework to analyze memory dumps for process hollowing, injected code via VAD
action: memory
  anomalies, hidden processes, and rootkit detection. Applies plugins like pslist, psscan, vadinfo, malfind, and dlllist to
  extract forensic artifacts from Windows memory images. Use during incident response memory analysis.

  '
domain: cybersecurity
subdomain: security-operations
tags:
- extracting
- memory
- artifacts
- with
version: '1.0'
author: dcx7c5
license: Apache-2.0
nist_csf:
- DE.CM-01
- RS.MA-01
- GV.OV-01
- DE.AE-02
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
source: Anthropic-Cybersecurity-Skills
mitre_attack:
- T1059
---

# Extracting Memory Artifacts with Rekall


## When to Use

- When performing authorized security testing that involves extracting memory artifacts with rekall
- When analyzing malware samples or attack artifacts in a controlled environment
- When conducting red team exercises or penetration testing engagements
- When building detection capabilities based on offensive technique understanding

## Prerequisites

- Familiarity with security operations concepts and tools
- Access to a test or lab environment for safe execution
- Python 3.8+ with required dependencies installed
- Appropriate authorization for any testing activities

## Instructions

Use Rekall to analyze memory dumps for signs of compromise including process
injection, hidden processes, and suspicious network connections.

```python
from rekall import session
from rekall import plugins

# Create a Rekall session with a memory image
s = session.Session(
    filename="/path/to/memory.raw",
    autodetect=["rsds"],
    profile_path=["https://github.com/google/rekall-profiles/raw/master"]
)

# List processes
for proc in s.plugins.pslist():
    print(proc)

# Detect injected code
for result in s.plugins.malfind():
    print(result)
```

Key analysis steps:
1. Load memory image and auto-detect profile
2. Run pslist and psscan to find hidden processes
3. Use malfind to detect injected/hollowed code in process VADs
4. Examine network connections with netscan
5. Extract suspicious DLLs and drivers with dlllist/modules

## Examples

```python
from rekall import session
s = session.Session(filename="memory.raw")
# Compare pslist vs psscan for hidden processes
pslist_pids = set(p.pid for p in s.plugins.pslist())
psscan_pids = set(p.pid for p in s.plugins.psscan())
hidden = psscan_pids - pslist_pids
print(f"Hidden PIDs: {hidden}")
```


---

## CyberSecSuite Integration

```bash
# Open a case before starting investigation
mcp__cybersec__case_open --title "memory" --type investigation

# Persist findings to PostgreSQL
mcp__cybersec__add_finding --title "..." --severity high --description "..."

# Log IOCs
mcp__cybersec__add_ioc --type domain --value "..." --confidence 0.9

# Map to MITRE
mcp__cybersec__suggest_mitre --description "..."
```

**Agent:** `@cybersec-agent` → delegates to appropriate specialist
