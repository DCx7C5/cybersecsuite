---
name: ntfs-alternate-data-stream-detect
description: >
  Detect NTFS Alternate Data Streams (ADS) used to hide malicious payloads, scripts, or executables behind legitimate files using Streams.exe and PowerShell.
action: detect
domain: cybersecurity
subdomain: filesystem-forensics
tags:
  - ntfs
  - ads
  - alternate-data-stream
  - steganography
  - hidden-data
  - streams
nist_csf:
  - DE.CM-04
  - DE.AE-02
mitre:
  - T1564.004
cwe:
  - CWE-706
capec: []
---
