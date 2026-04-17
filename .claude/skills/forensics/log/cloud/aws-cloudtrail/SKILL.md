---
name: performing-cloud-forensics-with-aws-cloudtrail
description: "Perform forensic investigation of AWS environments using CloudTrail logs to reconstruct attacker activity, identify"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-cloud-forensics-with-aws-cloudtrail/SKILL.md"
---
# Performing Cloud Forensics With Aws Cloudtrail

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-cloud-forensics-with-aws-cloudtrail/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-cloud-forensics-with-aws-cloudtrail", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-cloud-forensics-with-aws-cloudtrail")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cloud-security-analyst` or `@cybersec-agent`
