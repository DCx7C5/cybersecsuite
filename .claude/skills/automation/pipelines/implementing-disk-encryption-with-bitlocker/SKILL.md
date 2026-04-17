---
name: implementing-disk-encryption-with-bitlocker
description: "'Implements full disk encryption using Microsoft BitLocker on Windows endpoints to protect data at rest from"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-disk-encryption-with-bitlocker/SKILL.md"
---
# Implementing Disk Encryption With Bitlocker

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-disk-encryption-with-bitlocker/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-disk-encryption-with-bitlocker", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-disk-encryption-with-bitlocker")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
