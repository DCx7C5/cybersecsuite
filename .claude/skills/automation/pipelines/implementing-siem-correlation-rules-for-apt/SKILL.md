---
name: implementing-siem-correlation-rules-for-apt
description: "Write multi-event correlation rules that detect APT lateral movement by chaining Windows authentication events,"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-siem-correlation-rules-for-apt/SKILL.md"
---
# Implementing Siem Correlation Rules For Apt

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-siem-correlation-rules-for-apt/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-siem-correlation-rules-for-apt", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-siem-correlation-rules-for-apt")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
