---
name: detecting-dnp3-protocol-anomalies
description: "'Detect anomalies in DNP3 (Distributed Network Protocol 3) communications used in SCADA systems by monitoring"
domain: cybersecurity
subdomain: ot-ics-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-dnp3-protocol-anomalies/SKILL.md"
---
# Detecting Dnp3 Protocol Anomalies

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-dnp3-protocol-anomalies/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="detecting-dnp3-protocol-anomalies", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-dnp3-protocol-anomalies")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@ot-ics-security-analyst` or `@cybersec-agent`
