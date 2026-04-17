---
name: cassandra-auth-audit
description: >
  Audit Apache Cassandra authentication and authorization configuration, checking for AllowAll authenticator, default credentials, and JMX unauthenticated access.
action: audit
domain: cybersecurity
subdomain: database-security
tags:
  - cassandra
  - authentication
  - allowall
  - jmx
  - default-credentials
nist_csf:
  - ID.RA-01
  - PR.AC-03
mitre:
  - T1078
  - T1190
cwe:
  - CWE-306
---
