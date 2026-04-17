---
name: performing-linux-log-forensics-investigation
description: "Perform forensic investigation of Linux system logs including syslog, auth.log, systemd journal, kern.log, and"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-linux-log-forensics-investigation/SKILL.md"
---
# Performing Linux Log Forensics Investigation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-linux-log-forensics-investigation/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-linux-log-forensics-investigation", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-linux-log-forensics-investigation")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@digital-forensics-analyst` or `@cybersec-agent`
