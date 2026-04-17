---
name: analyzing-disk-image-with-autopsy
description: "Perform comprehensive forensic analysis of disk images using Autopsy to recover files, examine artifacts, and"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-disk-image-with-autopsy/SKILL.md"
---
# Analyzing Disk Image With Autopsy

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-disk-image-with-autopsy/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-disk-image-with-autopsy", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-disk-image-with-autopsy")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@digital-forensics-analyst` or `@cybersec-agent`
