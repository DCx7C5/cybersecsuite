---
name: mysql-injection-detect
description: >
  Detect SQL injection vulnerabilities in MySQL applications using sqlmap, manual payload testing, and query log analysis to identify blind and error-based injection points.
action: detect
domain: cybersecurity
subdomain: database-security
tags:
  - mysql
  - sql-injection
  - sqli
  - sqlmap
  - blind-sqli
  - error-based
nist_csf:
  - DE.CM-04
  - ID.RA-01
mitre:
  - T1190
  - T1505.003
cwe:
  - CWE-89
---
