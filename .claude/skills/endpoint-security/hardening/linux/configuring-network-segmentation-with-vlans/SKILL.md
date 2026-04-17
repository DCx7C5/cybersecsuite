---
name: configuring-network-segmentation-with-vlans
description: "'Designs and implements VLAN-based network segmentation on managed switches to isolate network zones, enforce"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-network-segmentation-with-vlans/SKILL.md"
---
# Configuring Network Segmentation With Vlans

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-network-segmentation-with-vlans/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="configuring-network-segmentation-with-vlans", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="configuring-network-segmentation-with-vlans")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
