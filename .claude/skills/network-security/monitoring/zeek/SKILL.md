---
name: detecting-dns-exfiltration-with-dns-query-analysis
description: "Detect data exfiltration through DNS tunneling by analyzing query entropy, subdomain length, query volume, TXT"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-dns-exfiltration-with-dns-query-analysis/SKILL.md"
---
# Detecting Dns Exfiltration With Dns Query Analysis

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-dns-exfiltration-with-dns-query-analysis/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="detecting-dns-exfiltration-with-dns-query-analysis", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-dns-exfiltration-with-dns-query-analysis")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@network-security-analyst` or `@cybersec-agent`
