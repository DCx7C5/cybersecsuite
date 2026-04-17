---
name: implementing-identity-verification-for-zero-trust
description: "Implement continuous identity verification for zero trust using phishing-resistant MFA (FIDO2/WebAuthn), risk-based"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-identity-verification-for-zero-trust/SKILL.md"
---
# Implementing Identity Verification For Zero Trust

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-identity-verification-for-zero-trust/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-identity-verification-for-zero-trust", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-identity-verification-for-zero-trust")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
