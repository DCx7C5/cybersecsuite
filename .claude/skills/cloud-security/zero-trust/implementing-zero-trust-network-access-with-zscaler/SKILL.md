---
name: implementing-zero-trust-network-access-with-zscaler
description: "Implement Zero Trust Network Access using Zscaler Private Access (ZPA) to replace traditional VPN with identity-based,"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-zero-trust-network-access-with-zscaler/SKILL.md"
---
# Implementing Zero Trust Network Access With Zscaler

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-zero-trust-network-access-with-zscaler/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-zero-trust-network-access-with-zscaler", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-zero-trust-network-access-with-zscaler")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
