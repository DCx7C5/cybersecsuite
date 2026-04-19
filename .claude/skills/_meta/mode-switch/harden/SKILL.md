---
name: mode-switch-harden
description: Switch CyberSecSuite between red-team (offensive) and blue-team (defensive) operating modes by patching settings.json. Controls agent model selection, destructive-action policy, validation strictness, and allowed tools.
domain: cybersecurity
subdomain: ops
tags:
- red-team
- blue-team
- configuration
- settings
- mode
mitre_attack: []
cve: []
cwe: []
nist_csf: []
capec: []
---
## Overview

Updates `.claude/settings.json` to activate red or blue team mode profiles. Red team: Opus model, non-destructive=false, relaxed validation, offensive tools unlocked. Blue team: defensive defaults, Sonnet model, strict IOC logging, cross-validation enforced.

## Usage

```
mode-switch red      — activate offensive (red team) mode
mode-switch blue     — activate defensive (blue team) mode
mode-switch status   — print current active mode
```

## Mode Differences

| Setting | Red Team | Blue Team |
|---|---|---|
| `default_model` | opus | sonnet |
| `non_destructive` | false | true |
| `cross_validation_min_sources` | 1 | 3 |
| `require_ioc_logging` | true | true |
| `require_mitre_mapping` | true | true |

## Notes

- Reads/writes `settings.json` at project root
- Does not restart ASGI server — model and policy changes apply on next agent invocation
- Pair with `/team-task` skill to route tasks to the correct team agent
