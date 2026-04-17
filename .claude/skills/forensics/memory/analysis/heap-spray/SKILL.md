---
name: analyzing-heap-spray-exploitation
description: "Detect and analyze heap spray attacks in memory dumps using Volatility3 plugins to identify NOP sled patterns,"
domain: cybersecurity
subdomain: malware-analysis
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-heap-spray-exploitation/SKILL.md"
---
# Analyzing Heap Spray Exploitation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-heap-spray-exploitation/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-heap-spray-exploitation", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-heap-spray-exploitation")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@malware-analysis-analyst` or `@cybersec-agent`
