---
name: building-threat-actor-profile-from-osint
description: "Build comprehensive threat actor profiles using open-source intelligence (OSINT) techniques to document adversary"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-threat-actor-profile-from-osint/SKILL.md"
---
# Building Threat Actor Profile From Osint

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-threat-actor-profile-from-osint/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-threat-actor-profile-from-osint", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-threat-actor-profile-from-osint")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
