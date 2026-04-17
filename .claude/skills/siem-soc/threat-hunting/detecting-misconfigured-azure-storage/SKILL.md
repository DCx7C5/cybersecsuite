---
name: detecting-misconfigured-azure-storage
description: "'Detecting misconfigured Azure Storage accounts including publicly accessible blob containers, missing encryption"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-misconfigured-azure-storage/SKILL.md"
---
# Detecting Misconfigured Azure Storage

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-misconfigured-azure-storage/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-misconfigured-azure-storage", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-misconfigured-azure-storage")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
