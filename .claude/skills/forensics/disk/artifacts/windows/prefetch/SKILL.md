---
name: analyzing-prefetch-files-for-execution-history
description: "Parse Windows Prefetch files to determine program execution history including run counts, timestamps, and referenced"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-prefetch-files-for-execution-history/SKILL.md"
---
# Analyzing Prefetch Files For Execution History

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-prefetch-files-for-execution-history/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-prefetch-files-for-execution-history", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-prefetch-files-for-execution-history")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@digital-forensics-analyst` or `@cybersec-agent`
