---
name: analyzing-threat-actor-ttps-with-mitre-attack
description: "MITRE ATT&CK is a globally-accessible knowledge base of adversary tactics, techniques, and procedures (TTPs)"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-threat-actor-ttps-with-mitre-attack/SKILL.md"
---
# Analyzing Threat Actor Ttps With Mitre Attack

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-threat-actor-ttps-with-mitre-attack/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-threat-actor-ttps-with-mitre-attack", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-threat-actor-ttps-with-mitre-attack")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@threat-intelligence-analyst` or `@cybersec-agent`
