---
name: detecting-exfiltration-over-dns-with-zeek
description: "Detect DNS-based data exfiltration by analyzing Zeek dns.log for high-entropy subdomains and anomalous query"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-exfiltration-over-dns-with-zeek/SKILL.md"
---
# Detecting Exfiltration Over Dns With Zeek

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-exfiltration-over-dns-with-zeek/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="detecting-exfiltration-over-dns-with-zeek", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-exfiltration-over-dns-with-zeek")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@network-security-analyst` or `@cybersec-agent`
