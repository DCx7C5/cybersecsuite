---
name: collecting-volatile-evidence-from-compromised-host
description: "Collect volatile forensic evidence from a compromised system following order of volatility, preserving memory,"
domain: cybersecurity
subdomain: incident-response
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/collecting-volatile-evidence-from-compromised-host/SKILL.md"
---
# Collecting Volatile Evidence From Compromised Host

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/collecting-volatile-evidence-from-compromised-host/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="collecting-volatile-evidence-from-compromised-host", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=)

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="collecting-volatile-evidence-from-compromised-host")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@incident-response-analyst` or `@cybersec-agent`
