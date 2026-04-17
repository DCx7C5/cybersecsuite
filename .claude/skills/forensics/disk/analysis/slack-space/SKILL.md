---
name: analyzing-slack-space-and-file-system-artifacts
description: "Examine file system slack space, MFT entries, USN journal, and alternate data streams to recover hidden data"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-slack-space-and-file-system-artifacts/SKILL.md"
---
# Analyzing Slack Space And File System Artifacts

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-slack-space-and-file-system-artifacts/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-slack-space-and-file-system-artifacts", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-slack-space-and-file-system-artifacts")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@digital-forensics-analyst` or `@cybersec-agent`
