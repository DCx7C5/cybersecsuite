---
name: configuring-host-based-intrusion-detection
description: "'Configures host-based intrusion detection systems (HIDS) to monitor endpoint file integrity, system calls, and"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-host-based-intrusion-detection/SKILL.md"
---
# Configuring Host Based Intrusion Detection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-host-based-intrusion-detection/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="configuring-host-based-intrusion-detection", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="configuring-host-based-intrusion-detection")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@endpoint-security-analyst` or `@cybersec-agent`
