---
name: configuring-hsm-for-key-storage
description: "Hardware Security Modules (HSMs) are tamper-resistant physical devices that safeguard cryptographic keys and"
domain: cybersecurity
subdomain: cryptography
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-hsm-for-key-storage/SKILL.md"
---
# Configuring Hsm For Key Storage

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-hsm-for-key-storage/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="configuring-hsm-for-key-storage", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="configuring-hsm-for-key-storage")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cryptography-analyst` or `@cybersec-agent`
