---
name: detecting-attacks-on-scada-systems
description: "'This skill covers detecting cyber attacks targeting Supervisory Control and Data Acquisition (SCADA) systems"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-attacks-on-scada-systems/SKILL.md"
---
# Detecting Attacks On Scada Systems

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-attacks-on-scada-systems/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="detecting-attacks-on-scada-systems", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-attacks-on-scada-systems")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@ot-ics-security-analyst` or `@cybersec-agent`
