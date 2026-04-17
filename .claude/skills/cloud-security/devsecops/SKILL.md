---
name: building-devsecops-pipeline-with-gitlab-ci
description: "Design and implement a comprehensive DevSecOps pipeline in GitLab CI/CD integrating SAST, DAST, container scanning,"
domain: cybersecurity
subdomain: devsecops
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-devsecops-pipeline-with-gitlab-ci/SKILL.md"
---
# Building Devsecops Pipeline With Gitlab Ci

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-devsecops-pipeline-with-gitlab-ci/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="building-devsecops-pipeline-with-gitlab-ci", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-devsecops-pipeline-with-gitlab-ci")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@devsecops-analyst` or `@cybersec-agent`
