---
name: analyzing-memory-forensics-with-lime-and-volatility
description: "'Performs Linux memory acquisition using LiME (Linux Memory Extractor) kernel module and analysis with Volatility"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-memory-forensics-with-lime-and-volatility/SKILL.md"
---
# Analyzing Memory Forensics With Lime And Volatility

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-memory-forensics-with-lime-and-volatility/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-memory-forensics-with-lime-and-volatility", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-memory-forensics-with-lime-and-volatility")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@security-operations-analyst` or `@cybersec-agent`
