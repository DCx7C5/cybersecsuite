---
name: analyzing-active-directory-acl-abuse
description: "Detect dangerous ACL misconfigurations in Active Directory using ldap3 to identify GenericAll, WriteDACL, and"
domain: cybersecurity
subdomain: identity-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-active-directory-acl-abuse/SKILL.md"
---
# Analyzing Active Directory Acl Abuse

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-active-directory-acl-abuse/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-active-directory-acl-abuse", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-active-directory-acl-abuse")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@identity-security-analyst` or `@cybersec-agent`
