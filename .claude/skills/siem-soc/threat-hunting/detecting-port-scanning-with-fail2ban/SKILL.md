---
name: detecting-port-scanning-with-fail2ban
description: "'Configures Fail2ban with custom filters and actions to detect port scanning activity, SSH brute force attempts,"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-port-scanning-with-fail2ban/SKILL.md"
---
# Detecting Port Scanning With Fail2Ban

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-port-scanning-with-fail2ban/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-port-scanning-with-fail2ban", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-port-scanning-with-fail2ban")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
