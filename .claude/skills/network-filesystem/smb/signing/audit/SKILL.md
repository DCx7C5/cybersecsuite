---
name: smb-signing-audit
description: >
  Audit SMB signing configuration across the network to identify hosts with signing disabled that are susceptible to NTLM relay and MitM attacks.
action: audit
domain: cybersecurity
subdomain: network-filesystem-security
tags:
  - smb-signing
  - ntlm-relay
  - crackmapexec
  - nmap-smb
  - network-hardening
nist_csf:
  - ID.RA-01
  - PR.DS-02
mitre:
  - T1557.001
---
