---
description: 'Advanced YARA rule optimization hook. Automatically optimizes generated rules for performance, false-positive reduction, metadata enrichment, and forensic best practices.'
---

# YaraRuleOptimization Hook – CyberSec Plugin

**Trigger:** `YARARuleOptimization` (recommended after generation, before testing)

**Purpose:**  
Takes raw YARA rules from `yara_rule_generator.py` and applies advanced optimization:
- Performance tuning (string ordering, condition complexity)
- False-positive reduction
- Rich metadata enrichment (MITRE, confidence, date)
- Modular rule structure with private rules
- Best-practice compliance

## What this hook does

1. Reads all `.yar` files in the session's `yara/` directory
2. Applies multiple optimization passes
3. Saves optimized versions as `optimized_*.yar`
4. Generates a detailed optimization report
5. Returns summary with improvements applied

## Advanced Optimization Techniques Used

- **String Reordering** — Most specific strings matched first
- **Condition Simplification** — `any of them`, `all of them`, reduced complexity
- **Fullword + Modifiers** — Added where appropriate for precision
- **Metadata Enrichment** — Author, date, investigation ID, MITRE tags, confidence
- **False-Positive Heuristics** — Common benign patterns excluded
- **Modular Design** — Private rules for internal reuse

## Usage

**From Claude:**
```bash
Run advanced YARA rule optimization on the current session