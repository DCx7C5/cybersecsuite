---
name: analyzing-mft-for-deleted-file-recovery
description: "Analyze the NTFS Master File Table ($MFT) to recover metadata and content of deleted files by examining MFT record"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-mft-for-deleted-file-recovery/SKILL.md"
---
# Analyzing Mft For Deleted File Recovery

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-mft-for-deleted-file-recovery/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-mft-for-deleted-file-recovery", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-mft-for-deleted-file-recovery")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@digital-forensics-analyst` or `@cybersec-agent`
