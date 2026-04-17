---
name: tmpfs-artifact-collect
description: >
  Collect volatile filesystem artifacts from tmpfs, /dev/shm, and /run before system shutdown, capturing malware drop zones and in-memory execution traces.
action: collect
domain: cybersecurity
subdomain: filesystem-forensics
tags:
  - tmpfs
  - devshm
  - volatile
  - artifact
  - memory-forensics
  - malware
nist_csf:
  - DE.AE-02
  - RS.AN-03
mitre:
  - T1036.005
  - T1564
---
