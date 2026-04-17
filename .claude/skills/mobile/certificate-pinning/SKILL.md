---
name: performing-mobile-app-certificate-pinning-bypass
description: "'Bypasses SSL/TLS certificate pinning implementations in Android and iOS applications to enable traffic interception"
domain: cybersecurity
subdomain: mobile-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-mobile-app-certificate-pinning-bypass/SKILL.md"
---
# Performing Mobile App Certificate Pinning Bypass

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-mobile-app-certificate-pinning-bypass/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-mobile-app-certificate-pinning-bypass", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-mobile-app-certificate-pinning-bypass")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@mobile-security-analyst` or `@cybersec-agent`
