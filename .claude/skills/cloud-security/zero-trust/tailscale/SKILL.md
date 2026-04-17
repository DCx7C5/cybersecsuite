---
name: deploying-tailscale-for-zero-trust-vpn
description: "Deploy and configure Tailscale as a WireGuard-based zero trust mesh VPN with identity-aware access controls,"
domain: cybersecurity
subdomain: zero-trust-architecture
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-tailscale-for-zero-trust-vpn/SKILL.md"
---
# Deploying Tailscale For Zero Trust Vpn

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-tailscale-for-zero-trust-vpn/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="deploying-tailscale-for-zero-trust-vpn", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="deploying-tailscale-for-zero-trust-vpn")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@zero-trust-architecture-analyst` or `@cybersec-agent`
