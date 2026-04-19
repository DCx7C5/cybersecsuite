---
name: android-adb-configure
description: >
  Configure ADB (Android Debug Bridge) connections for forensic device access, including USB and TCP/IP modes with proper permission controls.
domain: cybersecurity
subdomain: mobile-security
tags: [android, adb, mobile, forensics, configure]
nist_csf: [PR.AC-02]
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack: [T1418]
capec: []
---

# Android ADB Configure

## Overview

Configure Android Debug Bridge for forensic or red-team device access over USB or TCP/IP.

## Procedure

### USB Mode

```bash
adb devices           # list connected devices
adb shell             # open shell
adb pull /data/data/  # extract app data (requires root)
```

### TCP/IP Mode

```bash
adb tcpip 5555
adb connect <device-ip>:5555
adb shell
```

### Forensic acquisition

```bash
adb shell "cat /proc/version"
adb shell "getprop ro.build.version.release"
adb backup -all -f backup.ab
```

## MITRE ATT&CK

| Technique | Name |
|-----------|------|
| T1418 | Software Discovery |
