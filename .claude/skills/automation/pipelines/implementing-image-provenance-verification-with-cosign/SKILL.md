---
name: implementing-image-provenance-verification-with-cosign
description: "Sign and verify container image provenance using Sigstore Cosign with keyless OIDC-based signing, attestations,"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-image-provenance-verification-with-cosign/SKILL.md"
---
# Implementing Image Provenance Verification With Cosign

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-image-provenance-verification-with-cosign/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-image-provenance-verification-with-cosign", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-image-provenance-verification-with-cosign")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
