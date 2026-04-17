---
name: configuring-oauth2-authorization-flow
description: "Configure secure OAuth 2.0 authorization flows including Authorization Code with PKCE, Client Credentials, and"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-oauth2-authorization-flow/SKILL.md"
---
# Configuring Oauth2 Authorization Flow

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-oauth2-authorization-flow/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="configuring-oauth2-authorization-flow", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="configuring-oauth2-authorization-flow")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@identity-access-management-analyst` or `@cybersec-agent`
