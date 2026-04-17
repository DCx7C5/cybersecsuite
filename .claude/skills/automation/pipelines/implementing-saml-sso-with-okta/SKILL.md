---
name: implementing-saml-sso-with-okta
description: "Implement SAML 2.0 Single Sign-On (SSO) using Okta as the Identity Provider (IdP). This skill covers end-to-end"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-saml-sso-with-okta/SKILL.md"
---
# Implementing Saml Sso With Okta

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-saml-sso-with-okta/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-saml-sso-with-okta", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-saml-sso-with-okta")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
