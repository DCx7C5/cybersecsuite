---
name: conducting-memory-forensics-with-volatility
description: "'Performs memory forensics analysis using Volatility 3 to extract evidence of malware execution, process injection,"
domain: cybersecurity
subdomain: incident-response
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-memory-forensics-with-volatility/SKILL.md"
---
# Conducting Memory Forensics With Volatility

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-memory-forensics-with-volatility/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="conducting-memory-forensics-with-volatility", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=)

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="conducting-memory-forensics-with-volatility")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@incident-response-analyst` or `@cybersec-agent`
