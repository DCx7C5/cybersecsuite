---
name: deploying-cloudflare-access-for-zero-trust
description: "'Deploying Cloudflare Access with Cloudflare Tunnel to provide zero trust access to self-hosted and private applications,"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-cloudflare-access-for-zero-trust/SKILL.md"
---
# Deploying Cloudflare Access For Zero Trust

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-cloudflare-access-for-zero-trust/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="deploying-cloudflare-access-for-zero-trust", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="deploying-cloudflare-access-for-zero-trust")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@zero-trust-architecture-analyst` or `@cybersec-agent`
