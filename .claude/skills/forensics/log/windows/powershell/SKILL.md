---
name: analyzing-powershell-script-block-logging
description: "Parse Windows PowerShell Script Block Logs (Event ID 4104) from EVTX files to detect obfuscated commands, encoded"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-powershell-script-block-logging/SKILL.md"
---
# Analyzing Powershell Script Block Logging

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-powershell-script-block-logging/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-powershell-script-block-logging", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-powershell-script-block-logging")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@security-operations-analyst` or `@cybersec-agent`
