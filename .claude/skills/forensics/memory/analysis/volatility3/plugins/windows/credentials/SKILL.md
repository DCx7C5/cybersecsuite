---
name: analyzing-memory-dumps-with-volatility
description: "'Analyzes RAM memory dumps from compromised systems using the Volatility framework to identify malicious processes,"
domain: cybersecurity
subdomain: malware-analysis
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-memory-dumps-with-volatility/SKILL.md"
---
# Analyzing Memory Dumps With Volatility

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-memory-dumps-with-volatility/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-memory-dumps-with-volatility", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=)

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-memory-dumps-with-volatility")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@malware-analysis-analyst` or `@cybersec-agent`
