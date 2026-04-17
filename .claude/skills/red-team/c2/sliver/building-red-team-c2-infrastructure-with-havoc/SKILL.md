---
name: building-red-team-c2-infrastructure-with-havoc
description: "Deploy and configure the Havoc C2 framework with teamserver, HTTPS listeners, redirectors, and Demon agents for"
domain: cybersecurity
subdomain: red-teaming
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-red-team-c2-infrastructure-with-havoc/SKILL.md"
---
# Building Red Team C2 Infrastructure With Havoc

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-red-team-c2-infrastructure-with-havoc/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-red-team-c2-infrastructure-with-havoc", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-red-team-c2-infrastructure-with-havoc")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
