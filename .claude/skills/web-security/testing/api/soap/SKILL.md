---
name: performing-soap-web-service-security-testing
description: "Perform security testing of SOAP web services by analyzing WSDL definitions and testing for XML injection, XXE,"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-soap-web-service-security-testing/SKILL.md"
---
# Performing Soap Web Service Security Testing

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-soap-web-service-security-testing/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-soap-web-service-security-testing", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-soap-web-service-security-testing")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@api-security-analyst` or `@cybersec-agent`
