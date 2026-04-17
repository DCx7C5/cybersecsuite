---
name: implementing-passwordless-authentication-with-fido2
description: "Deploy FIDO2/WebAuthn passwordless authentication using security keys and platform authenticators. Covers WebAuthn"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-passwordless-authentication-with-fido2/SKILL.md"
---
# Implementing Passwordless Authentication With Fido2

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-passwordless-authentication-with-fido2/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-passwordless-authentication-with-fido2", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-passwordless-authentication-with-fido2")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
