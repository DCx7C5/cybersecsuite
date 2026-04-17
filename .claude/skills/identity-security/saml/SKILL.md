---
name: building-identity-federation-with-saml-azure-ad
description: "Establish SAML 2.0 identity federation between on-premises Active Directory and Azure AD (Microsoft Entra ID)"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-identity-federation-with-saml-azure-ad/SKILL.md"
---
# Building Identity Federation With Saml Azure Ad

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-identity-federation-with-saml-azure-ad/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="building-identity-federation-with-saml-azure-ad", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-identity-federation-with-saml-azure-ad")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@identity-access-management-analyst` or `@cybersec-agent`
