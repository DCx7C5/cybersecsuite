---
name: hidden-dotfile-detect
description: >
  Detect hidden files, dot-files, and persistence implants in home directories, /tmp, and writable paths used to conceal malware, scripts, and credentials.
action: detect
domain: cybersecurity
subdomain: filesystem-forensics
tags:
  - hidden-files
  - dotfile
  - persistence
  - malware
  - concealment
nist_csf:
  - DE.CM-04
  - DE.AE-02
mitre:
  - T1564.001
  - T1036
capec: []
---
