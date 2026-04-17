---
name: configuring-aws-verified-access-for-ztna
description: "Configure AWS Verified Access to provide VPN-less zero trust network access to internal applications using identity"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-aws-verified-access-for-ztna/SKILL.md"
---
# Configuring Aws Verified Access For Ztna

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-aws-verified-access-for-ztna/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="configuring-aws-verified-access-for-ztna", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="configuring-aws-verified-access-for-ztna")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@zero-trust-architecture-analyst` or `@cybersec-agent`
