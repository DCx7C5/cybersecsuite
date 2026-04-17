---
name: configuring-snort-ids-for-intrusion-detection
description: "'Installs, configures, and tunes Snort 3 intrusion detection system to monitor network traffic for malicious"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-snort-ids-for-intrusion-detection/SKILL.md"
---
# Configuring Snort Ids For Intrusion Detection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-snort-ids-for-intrusion-detection/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="configuring-snort-ids-for-intrusion-detection", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="configuring-snort-ids-for-intrusion-detection")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@network-security-analyst` or `@cybersec-agent`
