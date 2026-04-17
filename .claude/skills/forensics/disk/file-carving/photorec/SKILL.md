---
name: recovering-deleted-files-with-photorec
description: "Recover deleted files from disk images and storage media using PhotoRec's file signature-based carving engine"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/recovering-deleted-files-with-photorec/SKILL.md"
---
# Recovering Deleted Files With Photorec

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/recovering-deleted-files-with-photorec/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="recovering-deleted-files-with-photorec", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="recovering-deleted-files-with-photorec")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@digital-forensics-analyst` or `@cybersec-agent`
