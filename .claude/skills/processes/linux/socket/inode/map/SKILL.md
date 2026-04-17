---
name: linux-socket-inode-map
description: >
  Map Linux network socket inodes from /proc/<PID>/net/tcp to process PIDs for attributing network connections to specific processes and detecting hidden listeners.
action: map
domain: cybersecurity
subdomain: process-forensics
tags:
  - socket-inode
  - network-connection
  - proc-net
  - pid-mapping
  - hidden-listener
nist_csf:
  - DE.CM-01
  - DE.AE-02
mitre:
  - T1049
  - T1014
---
