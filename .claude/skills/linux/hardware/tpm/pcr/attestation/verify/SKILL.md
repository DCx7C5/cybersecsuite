
---
name: hardware-tpm-pcr-attestation-verify
description: Verify TPM PCR values and perform remote attestation to confirm system boot integrity — detect PCR tampering indicating bootkit or firmware compromise.
domain: cybersecurity
subdomain: hardware-security
tags:
- linux
- tpm
- pcr
- attestation
- secure-boot
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542.001
capec: []
---
# Hardware Tpm Pcr Attestation Verify
## Overview
This skill verifies the integrity and authenticity of attestation. Verify TPM PCR values and perform remote attestation to confirm system boot integrity — detect PCR tampering indicating bootkit or firmware compromise.
## When to Use
- When investigating or working with attestation in a hardware and firmware security context
- When verifying integrity of attestation
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: tpm2-tools, tss2, /dev/tpm0
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for hardware-tpm-pcr-attestation-verify
```
## Forensic Workflow
1. Identify scope — determine what attestation elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| attestation indicator | T1542.001 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "hardware-tpm-pcr-attestation-verify" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
