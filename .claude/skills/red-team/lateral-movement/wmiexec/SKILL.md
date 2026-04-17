---
name: performing-lateral-movement-with-wmiexec
description: "Perform lateral movement across Windows networks using WMI-based remote execution techniques including Impacket"
domain: cybersecurity
subdomain: red-teaming
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-lateral-movement-with-wmiexec/SKILL.md"
---
# Performing Lateral Movement With Wmiexec

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-lateral-movement-with-wmiexec/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-lateral-movement-with-wmiexec", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-lateral-movement-with-wmiexec")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@red-teaming-analyst` or `@cybersec-agent`
