---
name: performing-mobile-device-forensics-with-cellebrite
description: "Acquire and analyze mobile device data using Cellebrite UFED and open-source tools to extract communications,"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-mobile-device-forensics-with-cellebrite/SKILL.md"
---
# Performing Mobile Device Forensics With Cellebrite

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-mobile-device-forensics-with-cellebrite/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-mobile-device-forensics-with-cellebrite", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-mobile-device-forensics-with-cellebrite")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@digital-forensics-analyst` or `@cybersec-agent`
