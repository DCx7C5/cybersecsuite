---
name: extracting-credentials-from-memory-dump
description: "Extract cached credentials, password hashes, Kerberos tickets, and authentication tokens from memory dumps using"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/extracting-credentials-from-memory-dump/SKILL.md"
---
# Extracting Credentials From Memory Dump

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/extracting-credentials-from-memory-dump/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="extracting-credentials-from-memory-dump", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="extracting-credentials-from-memory-dump")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
