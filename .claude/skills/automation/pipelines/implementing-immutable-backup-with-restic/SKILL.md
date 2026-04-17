---
name: implementing-immutable-backup-with-restic
description: "'Implements immutable backup strategy using restic with S3-compatible storage and object lock for ransomware-resistant"
domain: cybersecurity
subdomain: ransomware-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-immutable-backup-with-restic/SKILL.md"
---
# Implementing Immutable Backup With Restic

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-immutable-backup-with-restic/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-immutable-backup-with-restic", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-immutable-backup-with-restic")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
