---
name: building-incident-timeline-with-timesketch
description: "Build collaborative forensic incident timelines using Timesketch to ingest, normalize, and analyze multi-source"
domain: cybersecurity
subdomain: incident-response
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-incident-timeline-with-timesketch/SKILL.md"
---
# Building Incident Timeline With Timesketch

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-incident-timeline-with-timesketch/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="building-incident-timeline-with-timesketch", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=)

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-incident-timeline-with-timesketch")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@incident-response-analyst` or `@cybersec-agent`
