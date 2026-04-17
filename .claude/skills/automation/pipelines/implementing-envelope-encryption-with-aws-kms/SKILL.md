---
name: implementing-envelope-encryption-with-aws-kms
description: "Envelope encryption is a strategy where data is encrypted with a data encryption key (DEK), and the DEK itself"
domain: cybersecurity
subdomain: cryptography
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-envelope-encryption-with-aws-kms/SKILL.md"
---
# Implementing Envelope Encryption With Aws Kms

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-envelope-encryption-with-aws-kms/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-envelope-encryption-with-aws-kms", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-envelope-encryption-with-aws-kms")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
