---
name: executing-active-directory-attack-simulation
description: "'Executes authorized attack simulations against Active Directory environments to identify misconfigurations,"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/executing-active-directory-attack-simulation/SKILL.md"
---
# Executing Active Directory Attack Simulation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/executing-active-directory-attack-simulation/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="executing-active-directory-attack-simulation", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="executing-active-directory-attack-simulation")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
