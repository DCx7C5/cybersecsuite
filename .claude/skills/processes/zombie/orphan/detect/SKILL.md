---
name: zombie-orphan-detect
description: >
  Detect zombie and orphan processes indicating crashed services, fork bombs, or malware that intentionally creates orphans to evade parent-process correlation.
action: detect
domain: cybersecurity
subdomain: process-forensics
tags:
  - zombie-process
  - orphan
  - fork-bomb
  - process-lifecycle
  - linux
nist_csf:
  - DE.CM-04
  - DE.AE-02
mitre:
  - T1014
capec: []
---
