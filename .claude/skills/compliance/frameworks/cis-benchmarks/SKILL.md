---
name: auditing-cloud-with-cis-benchmarks
description: "'This skill details how to conduct cloud security audits using Center for Internet Security benchmarks for AWS,"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/auditing-cloud-with-cis-benchmarks/SKILL.md"
---
# Auditing Cloud With Cis Benchmarks

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/auditing-cloud-with-cis-benchmarks/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="auditing-cloud-with-cis-benchmarks", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="auditing-cloud-with-cis-benchmarks")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cloud-security-analyst` or `@cybersec-agent`
