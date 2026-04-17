---
description: 'Comprehensive, non-destructive YARA rule testing hook for MalwareHunter. Tests generated rules against session artefacts, logs results, and produces audit-ready reports.'
---

# YaraRuleTesting Hook – CyberSec Plugin

**Trigger:** `YARATesting` (can be called manually, from PhaseEnd, or InvestigationEnd)

**Purpose:**  
Automatically test all generated YARA rules against the current session's artefacts and produce a full forensic test report.

## What this hook does

1. Finds all `.yar` files in `$SESSION_DIR/<investigation_id>/yara/`
2. Runs each rule against:
   - `artefacts/` directory (network, processes, memory, logs, etc.)
   - `raw_dumps/`
   - `iocs.md` and `findings.md`
3. Records matches, errors, and performance
4. Saves a full JSON test report + human-readable summary
5. Returns results in `additionalContext`

## Usage

**From Claude:**
```bash
Run YARA rule testing on the current session