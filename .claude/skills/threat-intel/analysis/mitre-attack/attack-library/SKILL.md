---
name: building-attack-pattern-library-from-cti-reports
description: "Extract and catalog attack patterns from cyber threat intelligence reports into a structured STIX-based library"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-attack-pattern-library-from-cti-reports/SKILL.md"
---
# Building Attack Pattern Library From Cti Reports

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-attack-pattern-library-from-cti-reports/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="building-attack-pattern-library-from-cti-reports", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-attack-pattern-library-from-cti-reports")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@threat-intelligence-analyst` or `@cybersec-agent`
