---
name: implementing-network-access-control
description: "'Implements 802.1X port-based network access control using RADIUS authentication, PacketFence NAC, and switch"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-access-control/SKILL.md"
---
# Implementing Network Access Control

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-access-control/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-network-access-control", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-network-access-control")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
