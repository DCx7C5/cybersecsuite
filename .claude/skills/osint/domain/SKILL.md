---
name: analyzing-typosquatting-domains-with-dnstwist
description: "Detect typosquatting, homograph phishing, and brand impersonation domains using dnstwist to generate domain permutations"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-typosquatting-domains-with-dnstwist/SKILL.md"
---
# Analyzing Typosquatting Domains With Dnstwist

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-typosquatting-domains-with-dnstwist/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-typosquatting-domains-with-dnstwist", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-typosquatting-domains-with-dnstwist")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@threat-intelligence-analyst` or `@cybersec-agent`
