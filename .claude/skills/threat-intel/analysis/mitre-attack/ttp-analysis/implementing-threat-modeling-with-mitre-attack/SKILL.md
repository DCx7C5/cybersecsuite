---
name: implementing-threat-modeling-with-mitre-attack
description: "'Implements threat modeling using the MITRE ATT&CK framework to map adversary TTPs against organizational assets,"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-threat-modeling-with-mitre-attack/SKILL.md"
---
# Implementing Threat Modeling With Mitre Attack

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-threat-modeling-with-mitre-attack/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-threat-modeling-with-mitre-attack", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-threat-modeling-with-mitre-attack")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
