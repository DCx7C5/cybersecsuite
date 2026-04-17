---
name: cifs-credential-intercept
description: >
  Intercept CIFS/SMB credentials using Responder and network poisoning techniques to capture NTLMv1/v2 challenge-response hashes for offline cracking.
action: intercept
domain: cybersecurity
subdomain: network-filesystem-security
tags:
  - cifs
  - ntlmv2
  - responder
  - llmnr
  - nbns
  - credential-capture
nist_csf:
  - DE.CM-01
mitre:
  - T1557.001
  - T1040
cwe:
  - CWE-287
---
