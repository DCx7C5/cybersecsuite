---
name: chrome-password-extract
description: >
  Extract saved Chrome passwords from the Login Data SQLite database, decrypt DPAPI-protected credentials, and identify plaintext password exposure.
action: extract
domain: cybersecurity
subdomain: browser-forensics
tags:
  - chrome
  - password
  - login-data
  - dpapi
  - credential-theft
  - sqlite
nist_csf:
  - DE.AE-02
  - RS.AN-03
mitre:
  - T1555.003
  - T1552.001
cwe:
  - CWE-312
capec: []
---
