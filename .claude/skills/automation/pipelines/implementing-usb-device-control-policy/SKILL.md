---
name: implementing-usb-device-control-policy
description: "'Implements USB device control policies to restrict unauthorized removable media access on endpoints, preventing"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-usb-device-control-policy/SKILL.md"
---
# Implementing Usb Device Control Policy

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-usb-device-control-policy/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-usb-device-control-policy", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-usb-device-control-policy")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
