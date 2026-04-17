---
name: managing-cloud-identity-with-okta
description: "'This skill covers implementing Okta as a centralized identity provider for cloud environments, configuring SSO"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/managing-cloud-identity-with-okta/SKILL.md"
---
# Managing Cloud Identity With Okta

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/managing-cloud-identity-with-okta/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="managing-cloud-identity-with-okta", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="managing-cloud-identity-with-okta")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
