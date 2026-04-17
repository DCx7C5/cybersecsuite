---
name: implementing-cisa-zero-trust-maturity-model
description: "Implement the CISA Zero Trust Maturity Model v2.0 across the five pillars of identity, devices, networks, applications,"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-cisa-zero-trust-maturity-model/SKILL.md"
---
# Implementing Cisa Zero Trust Maturity Model

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-cisa-zero-trust-maturity-model/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-cisa-zero-trust-maturity-model", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-cisa-zero-trust-maturity-model")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
