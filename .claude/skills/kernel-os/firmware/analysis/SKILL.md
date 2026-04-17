---
name: performing-firmware-malware-analysis
description: "'Analyzes firmware images for embedded malware, backdoors, and unauthorized modifications targeting routers,"
domain: cybersecurity
subdomain: malware-analysis
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-firmware-malware-analysis/SKILL.md"
---
# Performing Firmware Malware Analysis

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-firmware-malware-analysis/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-firmware-malware-analysis", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-firmware-malware-analysis")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@malware-analysis-analyst` or `@cybersec-agent`
