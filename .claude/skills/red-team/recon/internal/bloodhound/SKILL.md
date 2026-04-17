---
name: conducting-internal-reconnaissance-with-bloodhound-ce
description: "Conduct internal Active Directory reconnaissance using BloodHound Community Edition to map attack paths, identify"
domain: cybersecurity
subdomain: red-teaming
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-internal-reconnaissance-with-bloodhound-ce/SKILL.md"
---
# Conducting Internal Reconnaissance With Bloodhound Ce

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-internal-reconnaissance-with-bloodhound-ce/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="conducting-internal-reconnaissance-with-bloodhound-ce", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="conducting-internal-reconnaissance-with-bloodhound-ce")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@red-teaming-analyst` or `@cybersec-agent`
