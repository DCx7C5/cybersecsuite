---
name: hidden-rootkit-detect
description: >
  Detect filesystem-level rootkit concealment using rkhunter, chkrootkit, cross-verification of /proc vs readdir output, and kernel module audit.
action: detect
domain: cybersecurity
subdomain: filesystem-forensics
tags:
  - rootkit
  - rkhunter
  - chkrootkit
  - proc-vs-readdir
  - kernel-module
nist_csf:
  - DE.CM-04
  - DE.AE-02
mitre:
  - T1014
  - T1542.003
capec: []
---
