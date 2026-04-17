---
name: mongodb-exposure-detect
description: >
  Detect unauthenticated MongoDB instances exposed on the internet using Shodan queries, nmap scanning, and Metasploit auxiliary modules for version fingerprinting.
action: detect
domain: cybersecurity
subdomain: database-security
tags:
  - mongodb
  - exposure
  - shodan
  - unauthenticated
  - data-exposure
nist_csf:
  - ID.RA-01
  - DE.CM-04
mitre:
  - T1190
  - T1078
cwe:
  - CWE-306
---
