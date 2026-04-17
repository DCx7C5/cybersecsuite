---
name: smb-relay-execute
description: >
  Execute NTLM relay attacks against SMB targets without signing using Responder and ntlmrelayx to capture hashes and relay credentials for lateral movement.
action: execute
domain: cybersecurity
subdomain: network-filesystem-security
tags:
  - smb-relay
  - ntlm-relay
  - responder
  - ntlmrelayx
  - impacket
  - lateral-movement
nist_csf:
  - DE.CM-01
mitre:
  - T1557.001
  - T1550.002
cwe:
  - CWE-287
capec: []
---
