---
name: implementing-iec-62443-security-zones
description: "'This skill covers designing and implementing security zones and conduits for industrial automation and control"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-iec-62443-security-zones/SKILL.md"
---
# Implementing Iec 62443 Security Zones

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-iec-62443-security-zones/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-iec-62443-security-zones", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-iec-62443-security-zones")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
