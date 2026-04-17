---
name: containing-active-breach
description: "'Executes containment strategies to stop active adversary operations and prevent lateral movement during a confirmed"
domain: cybersecurity
subdomain: incident-response
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/containing-active-breach/SKILL.md"
---
# Containing Active Breach

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/containing-active-breach/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="containing-active-breach", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=)

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="containing-active-breach")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@incident-response-analyst` or `@cybersec-agent`
