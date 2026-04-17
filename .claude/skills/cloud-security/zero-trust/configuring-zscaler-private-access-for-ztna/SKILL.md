---
name: configuring-zscaler-private-access-for-ztna
description: "'Configuring Zscaler Private Access (ZPA) to replace traditional VPN with zero trust network access by deploying"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-zscaler-private-access-for-ztna/SKILL.md"
---
# Configuring Zscaler Private Access For Ztna

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-zscaler-private-access-for-ztna/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="configuring-zscaler-private-access-for-ztna", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="configuring-zscaler-private-access-for-ztna")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
