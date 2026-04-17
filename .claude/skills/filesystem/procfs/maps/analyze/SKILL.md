---
name: procfs-maps-analyze
description: > 
  Analyse /proc/<PID>/maps entries to identify memory-mapped libraries, anonymous executable regions, and injected code segments indicating process compromise.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
  - procfs
  - proc-maps
  - memory-map
  - injection
  - anonymous-regions
nist_csf:
  - DE.CM-04
  - DE.AE-02
mitre:
  - T1055
  - T1620
capec: []
---
