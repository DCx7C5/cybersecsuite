---
name: implementing-dragos-platform-for-ot-monitoring
description: "'Deploy and configure the Dragos Platform for OT network monitoring, leveraging its 600+ industrial protocol"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-dragos-platform-for-ot-monitoring/SKILL.md"
---
# Implementing Dragos Platform For Ot Monitoring

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-dragos-platform-for-ot-monitoring/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-dragos-platform-for-ot-monitoring", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-dragos-platform-for-ot-monitoring")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
