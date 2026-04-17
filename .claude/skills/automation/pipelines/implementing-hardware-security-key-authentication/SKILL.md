---
name: implementing-hardware-security-key-authentication
description: "'Implements FIDO2/WebAuthn hardware security key authentication including registration ceremonies, authentication"
domain: cybersecurity
subdomain: identity-and-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-hardware-security-key-authentication/SKILL.md"
---
# Implementing Hardware Security Key Authentication

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-hardware-security-key-authentication/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-hardware-security-key-authentication", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-hardware-security-key-authentication")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
