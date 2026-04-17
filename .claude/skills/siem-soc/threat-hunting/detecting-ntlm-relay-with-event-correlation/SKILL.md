---
name: detecting-ntlm-relay-with-event-correlation
description: "'Detect NTLM relay attacks through Windows Security Event correlation by analyzing Event 4624 LogonType 3 for"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-ntlm-relay-with-event-correlation/SKILL.md"
---
# Detecting Ntlm Relay With Event Correlation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-ntlm-relay-with-event-correlation/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-ntlm-relay-with-event-correlation", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-ntlm-relay-with-event-correlation")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
