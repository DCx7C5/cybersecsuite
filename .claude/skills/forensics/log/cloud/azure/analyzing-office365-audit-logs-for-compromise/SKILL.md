---
name: analyzing-office365-audit-logs-for-compromise
description: "Parse Office 365 Unified Audit Logs via Microsoft Graph API to detect email forwarding rule creation, inbox delegation,"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-office365-audit-logs-for-compromise/SKILL.md"
---
# Analyzing Office365 Audit Logs For Compromise

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-office365-audit-logs-for-compromise/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="analyzing-office365-audit-logs-for-compromise", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-office365-audit-logs-for-compromise")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
