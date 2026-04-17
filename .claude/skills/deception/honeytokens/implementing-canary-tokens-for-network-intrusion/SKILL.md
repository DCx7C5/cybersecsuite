---
name: implementing-canary-tokens-for-network-intrusion
description: "'Deploys DNS, HTTP, and AWS API key canary tokens across network infrastructure to detect unauthorized access"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-canary-tokens-for-network-intrusion/SKILL.md"
---
# Implementing Canary Tokens For Network Intrusion

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-canary-tokens-for-network-intrusion/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-canary-tokens-for-network-intrusion", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-canary-tokens-for-network-intrusion")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
