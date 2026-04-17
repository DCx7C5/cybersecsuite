---
name: implementing-zero-trust-in-cloud
description: "'This skill guides organizations through implementing zero trust architecture in cloud environments following"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-zero-trust-in-cloud/SKILL.md"
---
# Implementing Zero Trust In Cloud

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-zero-trust-in-cloud/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-zero-trust-in-cloud", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-zero-trust-in-cloud")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
