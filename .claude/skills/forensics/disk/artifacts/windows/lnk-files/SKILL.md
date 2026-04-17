---
name: analyzing-lnk-file-and-jump-list-artifacts
description: "Analyze Windows LNK shortcut files and Jump List artifacts to establish evidence of file access, program execution,"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-lnk-file-and-jump-list-artifacts/SKILL.md"
---
# Analyzing Lnk File And Jump List Artifacts

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-lnk-file-and-jump-list-artifacts/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-lnk-file-and-jump-list-artifacts", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-lnk-file-and-jump-list-artifacts")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@digital-forensics-analyst` or `@cybersec-agent`
