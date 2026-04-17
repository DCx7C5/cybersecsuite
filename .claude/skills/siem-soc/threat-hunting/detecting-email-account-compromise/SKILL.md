---
name: detecting-email-account-compromise
description: "Detect compromised O365 and Google Workspace email accounts by analyzing inbox rule creation, suspicious sign-in"
domain: cybersecurity
subdomain: incident-response
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-email-account-compromise/SKILL.md"
---
# Detecting Email Account Compromise

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-email-account-compromise/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-email-account-compromise", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-email-account-compromise")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
