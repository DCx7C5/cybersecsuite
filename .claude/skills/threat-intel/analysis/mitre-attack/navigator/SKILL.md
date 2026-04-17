---
name: analyzing-apt-group-with-mitre-navigator
description: "Analyze advanced persistent threat (APT) group techniques using MITRE ATT&CK Navigator to create layered heatmaps"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-apt-group-with-mitre-navigator/SKILL.md"
---
# Analyzing Apt Group With Mitre Navigator

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-apt-group-with-mitre-navigator/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-apt-group-with-mitre-navigator", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-apt-group-with-mitre-navigator")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@threat-intelligence-analyst` or `@cybersec-agent`
