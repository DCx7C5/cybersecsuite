---
name: implementing-zero-trust-with-beyondcorp
description: "Deploy Google BeyondCorp Enterprise zero trust access controls using Identity-Aware Proxy (IAP), context-aware"
domain: cybersecurity
subdomain: zero-trust
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-zero-trust-with-beyondcorp/SKILL.md"
---
# Implementing Zero Trust With Beyondcorp

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-zero-trust-with-beyondcorp/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-zero-trust-with-beyondcorp", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-zero-trust-with-beyondcorp")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
