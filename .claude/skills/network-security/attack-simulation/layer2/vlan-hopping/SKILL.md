---
name: performing-vlan-hopping-attack
description: "'Simulates VLAN hopping attacks using switch spoofing and double tagging techniques in authorized environments"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-vlan-hopping-attack/SKILL.md"
---
# Performing Vlan Hopping Attack

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-vlan-hopping-attack/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-vlan-hopping-attack", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-vlan-hopping-attack")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@network-security-analyst` or `@cybersec-agent`
