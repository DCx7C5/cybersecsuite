---
name: mssql-token-impersonate
description: >
  Exploit MSSQL EXECUTE AS and impersonation grants to escalate privileges from a low-privileged SQL login to sysadmin role through token impersonation chains.
action: impersonate
domain: cybersecurity
subdomain: database-security
tags:
  - mssql
  - impersonation
  - execute-as
  - sysadmin
  - privilege-escalation
nist_csf:
  - DE.CM-04
mitre:
  - T1548
  - T1078.003
cwe:
  - CWE-269
---
