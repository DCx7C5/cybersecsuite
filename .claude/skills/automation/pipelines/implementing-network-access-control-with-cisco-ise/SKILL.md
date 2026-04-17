---
name: implementing-network-access-control-with-cisco-ise
description: "Deploy Cisco Identity Services Engine for 802.1X wired and wireless authentication, MAC Authentication Bypass,"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-access-control-with-cisco-ise/SKILL.md"
---
# Implementing Network Access Control With Cisco Ise

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-access-control-with-cisco-ise/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-network-access-control-with-cisco-ise", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-network-access-control-with-cisco-ise")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
