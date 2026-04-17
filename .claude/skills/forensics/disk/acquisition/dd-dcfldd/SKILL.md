---
name: acquiring-disk-image-with-dd-and-dcfldd
description: "Create forensically sound bit-for-bit disk images using dd and dcfldd while preserving evidence integrity through"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/acquiring-disk-image-with-dd-and-dcfldd/SKILL.md"
---
# Acquiring Disk Image With Dd And Dcfldd

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/acquiring-disk-image-with-dd-and-dcfldd/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="acquiring-disk-image-with-dd-and-dcfldd", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="acquiring-disk-image-with-dd-and-dcfldd")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@digital-forensics-analyst` or `@cybersec-agent`
