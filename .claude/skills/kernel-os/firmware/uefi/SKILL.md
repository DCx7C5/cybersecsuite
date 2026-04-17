---
name: analyzing-uefi-bootkit-persistence
description: "'Analyzes UEFI bootkit persistence mechanisms including firmware implants in SPI flash, EFI System Partition"
domain: cybersecurity
subdomain: firmware-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-uefi-bootkit-persistence/SKILL.md"
---
# Analyzing Uefi Bootkit Persistence

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-uefi-bootkit-persistence/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-uefi-bootkit-persistence", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-uefi-bootkit-persistence")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@firmware-security-analyst` or `@cybersec-agent`
