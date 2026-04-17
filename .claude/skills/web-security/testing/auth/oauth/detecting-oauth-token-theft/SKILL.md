---
name: detecting-oauth-token-theft
description: "'Detects and responds to OAuth token theft and replay attacks in cloud environments, focusing on Microsoft Entra"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-oauth-token-theft/SKILL.md"
---
# Detecting Oauth Token Theft

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-oauth-token-theft/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-oauth-token-theft", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-oauth-token-theft")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
