---
name: testing-oauth2-implementation-flaws
description: "'Tests OAuth 2.0 and OpenID Connect implementations for security flaws including authorization code interception,"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-oauth2-implementation-flaws/SKILL.md"
---
# Testing Oauth2 Implementation Flaws

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-oauth2-implementation-flaws/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="testing-oauth2-implementation-flaws", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="testing-oauth2-implementation-flaws")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@api-security-analyst` or `@cybersec-agent`
