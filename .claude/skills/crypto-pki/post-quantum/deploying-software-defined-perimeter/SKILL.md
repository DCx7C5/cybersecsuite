---
name: deploying-software-defined-perimeter
description: "Deploy a Software-Defined Perimeter using the CSA v2.0 specification with Single Packet Authorization, mutual"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-software-defined-perimeter/SKILL.md"
---
# Deploying Software Defined Perimeter

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-software-defined-perimeter/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="deploying-software-defined-perimeter", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="deploying-software-defined-perimeter")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
