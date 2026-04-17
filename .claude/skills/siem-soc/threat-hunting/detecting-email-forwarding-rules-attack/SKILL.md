---
name: detecting-email-forwarding-rules-attack
description: "Detect malicious email forwarding rules created by adversaries to maintain persistent access to email communications"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-email-forwarding-rules-attack/SKILL.md"
---
# Detecting Email Forwarding Rules Attack

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-email-forwarding-rules-attack/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-email-forwarding-rules-attack", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-email-forwarding-rules-attack")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
