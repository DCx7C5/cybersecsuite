---
name: performing-gcp-penetration-testing-with-gcpbucketbrute
description: "Perform GCP security testing using GCPBucketBrute for storage bucket enumeration, gcloud IAM privilege escalation"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-gcp-penetration-testing-with-gcpbucketbrute/SKILL.md"
---
# Performing Gcp Penetration Testing With Gcpbucketbrute

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-gcp-penetration-testing-with-gcpbucketbrute/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-gcp-penetration-testing-with-gcpbucketbrute", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-gcp-penetration-testing-with-gcpbucketbrute")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cloud-security-analyst` or `@cybersec-agent`
