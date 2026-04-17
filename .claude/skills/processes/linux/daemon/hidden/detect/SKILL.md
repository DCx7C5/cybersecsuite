---
name: linux-daemon-hidden-detect
description: >
  Detect hidden daemons and rogue services by cross-referencing /proc entries with systemd, sysvinit, and initd service lists to identify process hiding.
action: detect
domain: cybersecurity
subdomain: process-forensics
tags:
  - hidden-daemon
  - rogue-service
  - systemd
  - process-hiding
  - rootkit
  - linux
nist_csf:
  - DE.CM-04
  - DE.AE-02
mitre:
  - T1014
  - T1543.002
---
