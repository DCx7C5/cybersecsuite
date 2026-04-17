---
name: implementing-digital-signatures-with-ed25519
description: "Ed25519 is a high-performance digital signature algorithm using the Edwards curve Curve25519. It provides 128-bit"
domain: cybersecurity
subdomain: cryptography
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-digital-signatures-with-ed25519/SKILL.md"
---
# Implementing Digital Signatures With Ed25519

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-digital-signatures-with-ed25519/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-digital-signatures-with-ed25519", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-digital-signatures-with-ed25519")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
