---
name: implementing-log-integrity-with-blockchain
description: "Build an append-only log integrity chain using SHA-256 hash chaining for tamper detection. Each log entry is"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-log-integrity-with-blockchain/SKILL.md"
---
# Implementing Log Integrity With Blockchain

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-log-integrity-with-blockchain/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-log-integrity-with-blockchain", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-log-integrity-with-blockchain")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
