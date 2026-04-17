---
name: detecting-suspicious-oauth-application-consent
description: "Detect risky OAuth application consent grants in Azure AD / Microsoft Entra ID using Microsoft Graph API, audit"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-suspicious-oauth-application-consent/SKILL.md"
---
# Detecting Suspicious Oauth Application Consent

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-suspicious-oauth-application-consent/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-suspicious-oauth-application-consent", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-suspicious-oauth-application-consent")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
