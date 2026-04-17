---
description: 'Hook that automatically generates high-quality YARA rules from IOCs, findings, suspicious strings, memory patterns, and threat intelligence.'
---

# YaraRuleGeneration Hook – CyberSec Plugin

**Trigger:** `YARAGeneration` (called from IOCDiscovered, EvidenceCollected, ThreatDetected, or manually)

**Purpose:**  
Automatically generate production-ready YARA rules from the current investigation data and save them to the session's `yara/` folder + project-level archive.

## What this hook does

1. Reads current session IOCs, findings, and evidence
2. Generates high-quality, commented YARA rules
3. Saves rules to:
   - `$SESSION_DIR/<investigation_id>/yara/generated_rules_*.yar`
   - Project-level `yara/` archive
4. Returns the generated rules in `additionalContext` for immediate use

## Usage

**From Claude:**
```bash
Use the YARA rule generation hook with trigger="ioc_discovered"