---
name: implementing-aes-encryption-for-data-at-rest
description: "AES (Advanced Encryption Standard) is a symmetric block cipher standardized by NIST (FIPS 197) used to protect"
domain: cybersecurity
subdomain: cryptography
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aes-encryption-for-data-at-rest/SKILL.md"
---
# Implementing Aes Encryption For Data At Rest

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aes-encryption-for-data-at-rest/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-aes-encryption-for-data-at-rest", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-aes-encryption-for-data-at-rest")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
