---
name: performing-cloud-incident-containment-procedures
description: "Execute cloud-native incident containment across AWS, Azure, and GCP by isolating compromised resources, revoking"
domain: cybersecurity
subdomain: incident-response
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-cloud-incident-containment-procedures/SKILL.md"
---
# Performing Cloud Incident Containment Procedures

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-cloud-incident-containment-procedures/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-cloud-incident-containment-procedures", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=)

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-cloud-incident-containment-procedures")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@incident-response-analyst` or `@cybersec-agent`
