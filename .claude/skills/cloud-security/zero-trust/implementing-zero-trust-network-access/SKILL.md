---
name: implementing-zero-trust-network-access
description: "'Implementing Zero Trust Network Access (ZTNA) in cloud environments by configuring identity-aware proxies, micro-segmentation,"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-zero-trust-network-access/SKILL.md"
---
# Implementing Zero Trust Network Access

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-zero-trust-network-access/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-zero-trust-network-access", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-zero-trust-network-access")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
